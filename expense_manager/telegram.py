import hmac
import json

import frappe
import requests
from frappe.utils import getdate, nowdate

from expense_manager.expense_manager.doctype.expense.expense import get_budget, get_month_spend

TELEGRAM_API = "https://api.telegram.org"
OPENAI_API = "https://api.openai.com/v1"
EXTRACTION_PROMPT = (
    "Extract one expense from the user's text. Reply with JSON only: "
    '{"amount": number, "category": one of %s or null, "description": short string}.'
)


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


def download_voice(file_id):
    token = get_settings().get_password("telegram_bot_token")
    info = requests.get(
        f"{TELEGRAM_API}/bot{token}/getFile", params={"file_id": file_id}, timeout=10
    )
    info.raise_for_status()
    audio = requests.get(
        f"{TELEGRAM_API}/file/bot{token}/{info.json()['result']['file_path']}", timeout=30
    )
    audio.raise_for_status()
    return audio.content


def openai_headers():
    return {"Authorization": f"Bearer {get_settings().get_password('openai_api_key')}"}


def transcribe(audio):
    response = requests.post(
        f"{OPENAI_API}/audio/transcriptions",
        headers=openai_headers(),
        files={"file": ("voice.ogg", audio, "audio/ogg")},
        data={"model": "whisper-1"},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["text"]


def extract_expense(text):
    categories = frappe.get_all("Expense Category", pluck="name")
    response = requests.post(
        f"{OPENAI_API}/chat/completions",
        headers=openai_headers(),
        json={
            "model": "gpt-4o-mini",
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": EXTRACTION_PROMPT % json.dumps(categories)},
                {"role": "user", "content": text},
            ],
        },
        timeout=30,
    )
    response.raise_for_status()
    return json.loads(response.json()["choices"][0]["message"]["content"])


def record_expense(user, expense):
    return frappe.get_doc(
        {
            "doctype": "Expense",
            "amount": expense["amount"],
            "category": expense["category"],
            "description": expense["description"],
            "expense_date": nowdate(),
            "spent_by": user,
            "source": "Telegram",
        }
    ).insert()


def build_summary(expense):
    date = getdate(expense.expense_date)
    summary = f"Recorded {expense.amount:g} under {expense.category}."
    budget = get_budget(expense.spent_by, expense.category, date)
    if budget:
        spent = get_month_spend(expense.spent_by, date, expense.category)
        summary += f" {expense.category} budget: {spent:g} of {budget:g} used this month."
    return summary


def handle_voice(chat_id, user, voice):
    text = transcribe(download_voice(voice["file_id"]))
    expense = extract_expense(text)
    if not expense.get("amount") or not expense.get("category"):
        return send_message(chat_id, f'I heard "{text}" but could not find an amount and category.')
    send_message(chat_id, build_summary(record_expense(user, expense)))


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
        return send_message(
            chat_id, f"Your chat ID is {chat_id}. Ask the admin to link it to your account."
        )

    frappe.set_user(user)
    if "voice" in message:
        try:
            return handle_voice(chat_id, user, message["voice"])
        except Exception:
            frappe.log_error()
            return send_message(chat_id, "Could not process that voice note.")
    send_message(chat_id, "Send me a voice note describing your expense.")
