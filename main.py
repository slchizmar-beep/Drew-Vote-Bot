import requests
import time
from datetime import datetime
# ── Configuration ──────────────────────────────────────────────
TARGET_URL = "https://www.mahoningmatters.com/sports/article315099157.html"
INTERVAL = 30
LOG_FILE = "ping_log.txt"
# ───────────────────────────────────────────────────────────────
def ping(url: str) -> dict:
    """Send a GET request and return response time in ms, or an error."""
    try:
        start = time.perf_counter()
        response = requests.get(url, timeout=10)
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "status": response.status_code,
            "response_time_ms": round(elapsed_ms, 2),
            "error": None,
        }
    except requests.exceptions.Timeout:
        return {"status": None, "response_time_ms": None, "error": "Timeout"}
    except requests.exceptions.ConnectionError:
        return {"status": None, "response_time_ms": None, "error": "Connection error"}
    except requests.exceptions.RequestException as e:
        return {"status": None, "response_time_ms": None, "error": str(e)}
def log(entry: str, log_file: str) -> None:
    """Append a log entry to the log file and print it to the console."""
    print(entry)
    with open(log_file, "a") as f:
        f.write(entry + "\n")
def main():
    print(f"Ping bot started → {TARGET_URL} (every {INTERVAL}s)")
    print(f"Logging to: {LOG_FILE}\n")
    log(f"=== Ping bot started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===", LOG_FILE)
    log(f"Target: {TARGET_URL} | Interval: {INTERVAL}s", LOG_FILE)
    log("=" * 55, LOG_FILE)
    while True:
        result = ping(TARGET_URL)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if result["error"]:
            entry = f"[{timestamp}] ERROR — {result['error']}"
        else:
            entry = (
                f"[{timestamp}] "
                f"Status: {result['status']} | "
                f"Response time: {result['response_time_ms']} ms"
            )
        log(entry, LOG_FILE)
        time.sleep(INTERVAL)
if __name__ == "__main__":
    main()
