from playwright.sync_api import sync_playwright
import requests
import pandas as pd
import base64
import time

def solve_quiz(email, secret, url):
    print(f"[INFO] Solving quiz from URL: {url}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            time.sleep(3)  # Allow JavaScript to load content

            # Try to find embedded instructions or base64 text
            html = page.content()
            if "atob(`" in html:
                print("[INFO] Found base64 encoded question")
            else:
                print("[INFO] Normal quiz HTML page detected")

            # Extract question text (simulation logic)
            question = page.inner_text("body")
            print("[DEBUG] Question Text Extracted:")
            print(question[:500])

            # Simulate logic — if the quiz is a sum of 'value' column
            # Replace this with actual parsing when real quizzes are live
            answer = 12345  # placeholder for computed result

            # Find submit URL on page (demo pattern)
            submit_url = None
            for line in html.splitlines():
                if "https://" in line and "submit" in line:
                    submit_url = line.split('"')[1]
                    break

            if not submit_url:
                # Fallback demo URL
                submit_url = "https://tds-llm-analysis.s-anand.net/submit"

            print(f"[INFO] Submitting answer to: {submit_url}")

            payload = {
                "email": email,
                "secret": secret,
                "url": url,
                "answer": answer
            }

            resp = requests.post(submit_url, json=payload)
            print(f"[INFO] Submit Response: {resp.status_code} {resp.text}")

            browser.close()

    except Exception as e:
        print(f"[ERROR] Solver failed: {e}")
