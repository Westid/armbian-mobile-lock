# uart_logger.py
import serial
import sqlite3
import time
import signal
import sys


SERIAL_PORT = '/dev/serial0'
BAUD_RATE = 115200
DB_PATH = 'data.db'


# --- Инициализация БД (один раз при старте) ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            raw TEXT NOT NULL,
            processed TEXT
        )
    """)
    conn.commit()
    return conn


# --- Обработка одной строки ---
def process_line(line: str) -> str:
    """Здесь ваша логика: парсинг, преобразование, проверка и т.п."""
    # Пример: если TTGO шлёт "TEMP:23.5", достаём число
    if line.startswith("TEMP:"):
        try:
            value = float(line.split(":", 1)[1])
            return f"temp={value}"
        except ValueError:
            return "invalid_temp"
    return line  # без изменений


# --- Основной цикл ---
def main():
    conn = init_db()
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

    # Аккуратное завершение по Ctrl+C
    running = True
    def stop(sig, frame):
        nonlocal running
        running = False
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    print(f"Слушаю {SERIAL_PORT} @ {BAUD_RATE}...")
    try:
        while running:
            line = ser.readline()
            if not line:
                continue

            raw = line.decode('ascii', errors='replace').strip()
            if not raw:
                continue

            processed = process_line(raw)
            ts = time.strftime('%Y-%m-%d %H:%M:%S')

            conn.execute(
                "INSERT INTO messages (timestamp, raw, processed) VALUES (?, ?, ?)",
                (ts, raw, processed)
            )
            conn.commit()
            print(f"[{ts}] {raw!r} → {processed!r}")
    finally:
        ser.close()
        conn.close()
        print("Остановлено.")


if __name__ == "__main__":
    main()
