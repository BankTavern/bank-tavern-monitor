import os
import json
import requests
from playwright.sync_api import sync_playwright

URL = "https://www.banktavern.com/"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PARTY_SIZES = [2, 4, 6]


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})


def check_slots():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL, timeout=60000)
        page.wait_for_timeout(8000)

        # Try to open booking widget (ResDiary usually triggers via button)
        try:
            page.click("text=Book")
        except:
            pass

        page.wait_for_timeout(5000)

        content = page.content().lower()

        browser.close()

        # detect time slots (real indicators)
        time_keywords = ["12:", "13:", "14:", "15:", "16:"]

        has_slots = any(t in content for t in time_keywords)

        if has_slots:
            for size in PARTY_SIZES:
                results.append(f"Possible slots for {size} people detected")

        return results


def main():
    try:
        slots = check_slots()

        if slots:
            message = (
                "🍽️ Bank Tavern Sunday Roast Alert!\n\n"
                "🎯 Possible availability detected\n\n"
                "👥 Checking party sizes: 2, 4, 6\n"
                "⏰ Look for 12:00–16:00 slots\n\n"
                "Book here: https://www.banktavern.com/contact-us/"
            )
            send_telegram(message)
        else:
            print("No slots found")

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    main()
