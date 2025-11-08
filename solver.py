# solver.py
import time
import json
import requests
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import os

MAX_SECONDS = 3 * 60  # 3 minutes per original POST

# Simple safety check (block localhost/private IPs)
def is_safe_url(u):
    try:
        p = urlparse(u)
        host = p.hostname or ""
        if host.startswith("127.") or host.startswith("192.168.") or host == "localhost":
            return False
        return True
    except Exception:
        return False

def find_submit_url(text, html):
    # look for explicit /submit endpoints
    import re
    m = re.search(r'(https?://[^\s"\'<>]+/submit[^\s"\'<>]*)', text, re.I)
    if m:
        return m.group(1)
    m2 = re.search(r'(https?://[^\s"\'<>]*submit[^\s"\'<>]*)', text, re.I)
    if m2:
        return m2.group(1)
    # fallback: search anchor hrefs in html for 'submit'
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        if "submit" in a["href"]:
            return a["href"]
    return None

def try_parse_table_sum_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    for t in tables:
        # attempt to find header containing 'value'
        headers = [th.get_text(strip=True).lower() for th in t.find_all("th")]
        # try first row as header if no <th>
        if not headers:
            first_row = t.find("tr")
            if first_row:
                headers = [td.get_text(strip=True).lower() for td in first_row.find_all(["td","th"])]
        if headers:
            try:
                idx = next(i for i,h in enumerate(headers) if "value" in h)
            except StopIteration:
                idx = None
            rows = t.find_all("tr")
            s = 0.0
            if idx is not None:
                # start from 1 if header row present else 0
                start = 1 if t.find("th") else 0
                for r in rows[start:]:
                    cells = r.find_all(["td","th"])
                    if len(cells) > idx:
                        text = cells[idx].get_text(strip=True)
                        num = ''.join(ch for ch in text if ch in "0123456789.-,")
                        if num:
                            num = num.replace(",", "")
                            try:
                                s += float(num)
                            except:
                                pass
                return s
    return None

def try_parse_linked_csv_sum(page):
    # find anchors and try simple CSV/JSON downloads
    anchors = page.query_selector_all("a")
    for a in anchors:
        href = a.get_attribute("href") or ""
        if not href:
            continue
        if any(href.lower().endswith(ext) for ext in (".csv", ".json", ".txt")):
            try:
                resp = requests.get(href, timeout=20)
                if resp.status_code == 200:
                    content = resp.content
                    if href.lower().endswith(".csv") or href.lower().endswith(".txt"):
                        df = pd.read_csv(pd.io.common.BytesIO(content))
                        for col in df.columns:
                            if "value" in col.lower():
                                return float(df[col].sum())
                    elif href.lower().endswith(".json"):
                        j = resp.json()
                        # if list of dicts
                        if isinstance(j, list):
                            for k in (k for k in range(len(j))):
                                pass
                            # convert to dataframe if possible
                            try:
                                df = pd.DataFrame(j)
                                for col in df.columns:
                                    if "value" in col.lower():
                                        return float(df[col].sum())
                            except:
                                pass
            except Exception:
                pass
    return None

def compute_answer_from_page(page, page_url):
    html = page.content()
    text = page.inner_text("body") if page else ""
    # 1) Try to parse table sum in page
    s = try_parse_table_sum_from_html(html)
    if s is not None:
        return s
    # 2) Try linked CSV/JSON
    s2 = try_parse_linked_csv_sum(page)
    if s2 is not None:
        return s2
    # 3) Look for "Answer: ..." in page text
    import re
    m = re.search(r'answer\s*[:\-]\s*([0-9\.\-]+)', text, re.I)
    if m:
        try:
            return float(m.group(1))
        except:
            pass
    # 4) fallback: first numeric token
    m2 = re.search(r'([-]?\d[\d,]*\.?\d*)', text)
    if m2:
        try:
            return float(m2.group(1).replace(",", ""))
        except:
            pass
    return None

def post_answer(submit_url, payload):
    try:
        r = requests.post(submit_url, json=payload, timeout=20)
        try:
            return r.status_code, r.json()
        except:
            return r.status_code, {"text": r.text}
    except Exception as e:
        return None, {"error": str(e)}

def start_solve_background(email, secret, url):
    start = time.time()
    deadline = start + MAX_SECONDS
    if not is_safe_url(url):
        print("Blocked unsafe URL:", url)
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        current = url
        try:
            while current and time.time() < deadline:
                print("Visiting:", current)
                try:
                    page.goto(current, wait_until="networkidle", timeout=30000)
                except Exception as e:
                    print("Page load error:", e)
                time.sleep(0.3)  # let JS settle
                html = page.content()
                text = page.inner_text("body")
                submit_url = find_submit_url(text, html)
                if not submit_url:
                    print("Submit URL not found on page:", current)
                    break

                answer = compute_answer_from_page(page, current)
                print("Computed answer:", answer)

                payload = {"email": email, "secret": secret, "url": current, "answer": answer}
                code, resp_json = post_answer(submit_url, payload)
                print("Submit response code:", code, "body:", resp_json)

                if resp_json and isinstance(resp_json, dict) and resp_json.get("url"):
                    current = resp_json.get("url")
                    continue
                else:
                    break
        finally:
            try:
                page.close()
                browser.close()
            except:
                pass
    duration = time.time() - start
    print(f"Solve finished in {duration:.1f}s")
