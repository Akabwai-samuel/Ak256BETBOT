# bot.py
from keep_alive import keep_alive
import requests
import time

TOKEN = "8023702827:AAG-bwk7bMSWyK84KR7RY4m3bh_MdovLg54"
API_URL = f"https://api.telegram.org/bot{TOKEN}"

chat_modes = {}
historical_matches = [
    ("Finland U21", "Ukraine U21", 0.75, 0.70, "2-1", 0.85),
    ("Kolding IF", "FC Thy", 0.72, 0.66, "1-2", 0.79),
    ("Bodoe/Glimt", "AIK", 0.80, 0.85, "3-1", 0.90),
    # Add more as needed
]

def get_updates(offset=None):
    url = f"{API_URL}/getUpdates"
    params = {"timeout": 100, "offset": offset}
    r = requests.get(url, params=params)
    return r.json()

def send_message(chat_id, text):
    url = f"{API_URL}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    requests.post(url, data=data)

def filter_predictions(mode="safe"):
    safe_threshold = 0.7 if mode == "safe" else 0.5
    filtered = []
    for match in historical_matches:
        home, away, btts, over_25, cs, safe_goals = match
        if btts >= safe_threshold and over_25 >= safe_threshold:
            filtered.append(f"*{home} vs {away}*\nBTTS: Yes\nOver 2.5: Yes\nCorrect Score: {cs}\nSafe 2+ Goals: {safe_goals*100:.0f}%")
    return filtered

def handle_command(chat_id, command):
    if command == "/start":
        chat_modes[chat_id] = "safe"
        send_message(chat_id, "🎯 *Ak256BetBot Ready!*\nMode set to *Safe*.\nUse /mode safe or /mode aggressive\nUse /today to get predictions.")
    elif command.startswith("/mode"):
        mode = command.split(" ")[1] if len(command.split(" ")) > 1 else None
        if mode in ["safe", "aggressive"]:
            chat_modes[chat_id] = mode
            send_message(chat_id, f"Mode switched to *{mode.capitalize()}*.")
        else:
            send_message(chat_id, "Invalid mode. Use /mode safe or /mode aggressive.")
    elif command == "/today":
        mode = chat_modes.get(chat_id, "safe")
        predictions = filter_predictions(mode)
        if predictions:
            for pred in predictions:
                send_message(chat_id, pred)
        else:
            send_message(chat_id, "No predictions available today.")
    else:
        send_message(chat_id, "Unknown command. Use /start, /mode safe, /mode aggressive, or /today.")

def main():
    print("🔁 Bot is running...")
    offset = None
    while True:
        updates = get_updates(offset)
        if updates["ok"]:
            for update in updates["result"]:
                offset = update["update_id"] + 1
                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"]["text"]
                    if text.startswith("/"):
                        handle_command(chat_id, text)
        time.sleep(1)

if __name__ == "__main__":
    main()
keep_alive()
