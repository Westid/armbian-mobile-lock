FROM python:3.13-slim

WORKDIR /app

# Устанавливаем только необходимые системные пакеты
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

COPY . .
RUN pip install uv && uv sync

EXPOSE 8080
# Запускаем uvicorn с одним воркером
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
