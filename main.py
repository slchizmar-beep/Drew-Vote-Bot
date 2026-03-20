import requests
import time
import pyautogui
from datetime import datetime

# ── Configuration ──────────────────────────────────────────────
TARGET_URL    = "https://example.com"   # Change to your target URL
INTERVAL      = 60                      # Seconds between pings
LOG_FILE      = "ping_log.txt"          # Log file name
TARGET_IMAGE  = "target.png"            # Image file to find & click on screen
CONFIDENCE    = 0.8                     # Match confidence (0.0 – 1.0)
# ───────────────────────────────────────────────────────────────

def ping(url: str) -> dict:
    """Send a GET request and return response time in ms, or an error."""
    try:
        start = time.perf_counter()
        response = requests.get(url, timeout=30)
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


def find_and_click(image_path: str, confidence: float) -> str:
    """
    Locate the target image on screen and click its center.
    Returns a status string describing the outcome.
    """
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location is None:
            return "Image not found on screen"
        center = pyautogui.center(location)
        pyautogui.click(center)
        return f"Clicked at ({center.x}, {center.y})"
    except pyautogui.ImageNotFoundException:
        return "Image not found on screen"
    except Exception as e:
        return f"Click error: {e}"


def log(entry: str, log_file: str) -> None:
    """Append a log entry to the log file and print it to the console."""
    print(entry)
    with open(log_file, "a") as f:
        f.write(entry + "\n")


def main():
    print(f"Ping bot started → {TARGET_URL}  (every {INTERVAL}s)")
    print(f"Looking for image: {TARGET_IMAGE}")
    print(f"Logging to: {LOG_FILE}")
    print("TIP: Move mouse to top-left corner of screen to emergency-stop.\n")

    log(f"=== Ping bot started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===", LOG_FILE)
    log(f"Target URL: {TARGET_URL} | Image: {TARGET_IMAGE} | Interval: {INTERVAL}s", LOG_FILE)
    log("=" * 65, LOG_FILE)

    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # --- Ping ---
        result = ping(TARGET_URL)
        if result["error"]:
            ping_entry = f"[{timestamp}]  PING ERROR — {result['error']}"
        else:
            ping_entry = (
                f"[{timestamp}]  "
                f"Status: {result['status']}  |  "
                f"Response time: {result['response_time_ms']} ms"
            )

        # --- Click ---
        click_result = find_and_click(TARGET_IMAGE, CONFIDENCE)
        click_entry = f"[{timestamp}]  CLICK — {click_result}"

        log(ping_entry, LOG_FILE)
        log(click_entry, LOG_FILE)

        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
