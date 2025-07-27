import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "../log.txt")

def log(message, user=None):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_info = f" {{{user}}}" if user else ""
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}]{user_info} {message}\n")