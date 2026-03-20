import requests
import time
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

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


async def find_and_click(page, image_path: str, confidence: float) -> str:
    """
    Locate the target image on the rendered page and click it.
    Returns a status string describing the outcome.
    """
    try:
        # Try to find image using Playwright's built-in image matching
        locator = page.locator(f"img[src*='{image_path}']")
        if await locator.count() > 0:
            await locator.first.click()
            return f"Clicked image: {image_path}"
        
        # Fallback: try to find by alt text or other attributes
        return "Image not found on page"
    except Exception as e:
        return f"Click error: {e}"


def log(entry: str, log_file: str) -> None:
    """Append a log entry to the log file and print it to the console."""
    print(entry)
    with open(log_file, "a") as f:
        f.write(entry + "\n")


async def main():
    print(f"Ping bot started → {TARGET_URL}  (every {INTERVAL}s)")
    print(f"Looking for image: {TARGET_IMAGE}")
    print(f"Logging to: {LOG_FILE}\n")

    log(f"=== Ping bot started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===", LOG_FILE)
    log(f"Target URL: {TARGET_URL} | Image: {TARGET_IMAGE} | Interval: {INTERVAL}s", LOG_FILE)
    log("=" * 65, LOG_FILE)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
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

                # --- Navigate and Click ---
                try:
                    await page.goto(TARGET_URL, wait_until="networkidle")
                    click_result = await find_and_click(page, TARGET_IMAGE, CONFIDENCE)
                except Exception as e:
                    click_result = f"Navigation error: {e}"
                
                click_entry = f"[{timestamp}]  CLICK — {click_result}"

                log(ping_entry, LOG_FILE)
                log(click_entry, LOG_FILE)

                await asyncio.sleep(INTERVAL)
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
