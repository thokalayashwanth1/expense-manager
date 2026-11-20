import hmac

import frappe
import requests

TELEGRAM_API = "https://api.telegram.org"


def get_settings():
    return frappe.get_single("Expense Manager Settings")


def send_message(chat_id, text):
    token = get_settings().get_password("telegram_bot_token")
    requests.post(
        f"{TELEGRAM_API}/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=10,
    ).raise_for_status()


def get_user_by_chat_id(chat_id):
    return frappe.db.get_value("User", {"telegram_chat_id": str(chat_id)})


def is_valid_request():
    secret = get_settings().get_password("webhook_secret")
    received = frappe.get_request_header("X-Telegram-Bot-Api-Secret-Token") or ""
    return bool(secret) and hmac.compare_digest(secret, received)


@frappe.whitelist(allow_guest=True)
def webhook():
    if not is_valid_request():
        frappe.throw("Invalid secret", frappe.PermissionError)

    frappe.enqueue(process_update, update=frappe.request.get_json(), queue="short")


def process_update(update):
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    user = get_user_by_chat_id(chat_id)

    if not user:
        return send_message(chat_id, f"Your chat ID is {chat_id}. Ask the admin to link it to your account.")

    frappe.set_user(user)
    if "voice" in message:
        return send_message(chat_id, "Voice note received.")
    send_message(chat_id, "Send me a voice note describing your expense.")
