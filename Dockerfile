FROM python:3.10-slim

WORKDIR /app

# Устанавливаем только необходимые системные пакеты
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запускаем uvicorn с одним воркером
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
