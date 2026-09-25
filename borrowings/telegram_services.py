import os
import requests


def send_telegram_notification(message):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error:{e}")
