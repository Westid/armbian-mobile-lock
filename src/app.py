# uart_logger.py
import serial
import sqlite3
import signal
from datetime import datetime
from string import ascii_letters


SERIAL_PORT = '/dev/ttyV0'
BAUD_RATE = 9600
DB_PATH = '/app/data/data.db'


# --- Инициализация БД (один раз при старте) ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type WARCHAR NOT NULL,
            box_num INT NOT NULL,
            box_event_num INT NOT NULL,
            state INT NOT NULL,
            battery_mv INT,
            ts TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


# --- Обработка одной строки ---
def process_line(line: str) -> str:
    """Здесь ваша логика: парсинг, преобразование, проверка и т.п."""
    # Пример: если TTGO шлёт "TEMP:23.5", достаём число
    e, box, event, state, battery_mv = map(
        lambda x: int(x) if x not in ascii_letters else x, line.split(',')
    )
    return e, box, event, state, battery_mv


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
        while ser.readable():
            line = ser.readline()
            ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.3f")
            if not line:
                continue

            raw = line.decode('ascii', errors='replace').strip()
            if not raw:
                continue

            event_type, box_num, box_event_num, state, battery_mv = process_line(raw)

            conn.execute(
                "INSERT INTO messages (event_type, box_num, box_event_num, state, battery_mv, ts) VALUES (?, ?, ?, ?, ?, ?)",
                (event_type, box_num, box_event_num, state, battery_mv, ts)
            )
            conn.commit()
            print(f"[{ts}] {raw!r} → {event_type, box_num, box_event_num, state, battery_mv, ts!r}")
    finally:
        ser.close()
        conn.close()
        print("Остановлено.")


if __name__ == "__main__":
    main()
