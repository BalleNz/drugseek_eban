FROM python:3.12-slim

WORKDIR /drug_search

ENV PYTHONPATH=/drug_search

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Кэшируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY drug_search/asgi.py .
COPY . .