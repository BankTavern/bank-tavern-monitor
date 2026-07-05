import os
import requests
from playwright.sync_api import sync_playwright

# ===== CONFIG =====
BOOKING_URL = "https://www.banktavern.com/contact-us/"  # we will refine this later
TARGET_KEYWORD = "Sunday"  # simple first version
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload)


def check_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(BOOKING_URL, timeout=60000)
        content = page.content()

        browser.close()

        return TARGET_KEYWORD.lower() in content.lower()


def main():
    try:
        available = check_page()

        if available:
            send_telegram("🍽️ Possible Sunday roast availability detected at The Bank Tavern!\n\nCheck now: https://www.banktavern.com/")
        else:
            print("No availability found.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
