FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (kept minimal)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project
COPY . .

# Default model path (can be overridden at runtime with TELEGRAM_MODEL_PATH env var)
ENV TELEGRAM_MODEL_PATH=/app/models/poisson_baseline.joblib

# Run the Telegram bot
CMD ["python", "bot/telegram_bot.py"]
