import os
import json
import requests
from playwright.sync_api import sync_playwright

BOOKING_URL = "https://www.banktavern.com/"
TARGET_KEYWORD = "sunday"

STATE_FILE = "state.json"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"last_alerted": False}
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def check_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(BOOKING_URL, timeout=60000)

        # wait for booking widget to fully load
        page.wait_for_timeout(7000)

        content = page.content().lower()

        browser.close()

        # STRONG indicators of real availability
        positive_signals = [
            "select a time",
            "choose a time",
            "12:",
            "13:",
            "14:",
            "available times"
        ]

        # STRONG indicators of no availability
        negative_signals = [
            "no availability",
            "fully booked",
            "no tables available",
            "try another date"
        ]

        has_positive = any(x in content for x in positive_signals)
        has_negative = any(x in content for x in negative_signals)

        # Only alert if we see positive signals AND no negative signals
        return has_positive and not has_negative


def main():
    state = load_state()
    available = check_page()

    # If availability detected and we haven't alerted yet
    if available and not state.get("last_alerted"):
        send_telegram(
            "🍽️ Possible Bank Tavern Sunday roast availability detected!\n\nCheck: https://www.banktavern.com/"
        )
        state["last_alerted"] = True
        save_state(state)

    # Reset state if nothing found (so future alerts work again)
    if not available:
        state["last_alerted"] = False
        save_state(state)

    print("Check complete:", available)


if __name__ == "__main__":
    main()
