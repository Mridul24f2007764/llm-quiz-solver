FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y curl libnss3 libatk1.0-0 libatk-bridge2.0-0 libx11-xcb1 libxcb1 libxcomposite1 libxdamage1 libxrandr2 libgbm-dev libasound2 libpangocairo-1.0-0 libcups2 libdrm2 && \
    pip install --upgrade pip && pip install -r requirements.txt && python -m playwright install --with-deps

COPY . .

ENV PORT=5000
EXPOSE 5000
CMD ["python", "server.py"]
