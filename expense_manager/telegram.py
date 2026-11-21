import base64
import hmac
import json
import secrets

import frappe
import requests
from frappe.utils import get_fullname, getdate
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from expense_manager.expense_manager.doctype.dependent.dependent import get_pocket_money_balance
from expense_manager.expense_manager.doctype.expense.expense import (
    allowed_categories_for,
    create_expense,
    get_budget,
    get_month_spend,
)

TELEGRAM_API = "https://api.telegram.org"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent"
LINK_CODE_TTL = 600
EXTRACTION_PROMPT = (
    "Extract one expense from the user's text. Reply with JSON only: "
    '{"amount": number, "category": one of %s or null, "description": short string, '
    '"person": one of %s if the text clearly says the expense is for that person, otherwise null}.'
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


def gemini_session():
    session = requests.Session()
    retry = Retry(
        total=4,
        backoff_factor=2,
        status_forcelist=[429, 500, 503],
        allowed_methods=["POST"],
        raise_on_status=False,
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def generate(parts, **body):
    response = gemini_session().post(
        GEMINI_URL,
        headers={"x-goog-api-key": get_settings().get_password("gemini_api_key")},
        json={"contents": [{"parts": parts}], **body},
        timeout=25,
    )
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()


def transcribe(audio):
    return generate(
        [
            {"text": "Transcribe this audio. Reply with the transcript only."},
            {"inline_data": {"mime_type": "audio/ogg", "data": base64.b64encode(audio).decode()}},
        ]
    )


def extract_expense(text, categories, people):
    prompt = EXTRACTION_PROMPT % (json.dumps(categories), json.dumps(people))
    return json.loads(
        generate(
            [{"text": text}],
            system_instruction={"parts": [{"text": prompt}]},
            generationConfig={"responseMimeType": "application/json"},
        )
    )


def get_family_members(user):
    members = frappe.get_all(
        "Dependent", filters={"parent_user": user}, fields=["dependent_name", "user"]
    )
    return {member.dependent_name: member.user for member in members}


def build_summary(expense):
    date = getdate(expense.expense_date)
    summary = f"Recorded {expense.amount:g} under {expense.category} for {get_fullname(expense.spent_by)}."
    budget = get_budget(expense.spent_by, expense.category, date)
    if budget:
        spent = get_month_spend(expense.spent_by, date, expense.category)
        summary += f" {expense.category} budget: {spent:g} of {budget:g} used this month."
    dependent = frappe.db.get_value("Dependent", {"user": expense.spent_by})
    if dependent:
        summary += f" Pocket money left: {get_pocket_money_balance(dependent)['balance']:g}."
    return summary


def handle_voice(chat_id, user, voice):
    text = transcribe(download_voice(voice["file_id"]))
    members = get_family_members(user)
    expense = extract_expense(text, allowed_categories_for(user), list(members))
    if not expense.get("amount") or not expense.get("category"):
        return send_message(chat_id, f'I heard "{text}" but could not find an amount and category.')

    payer = members.get(expense.get("person"), user)
    if expense["category"] not in allowed_categories_for(payer):
        return send_message(chat_id, f"{expense['category']} is not available for {get_fullname(payer)}.")

    doc = create_expense(payer, expense["category"], expense["amount"], expense["description"], "Telegram")
    send_message(chat_id, build_summary(doc))


@frappe.whitelist(allow_guest=True)
def webhook():
    if not is_valid_request():
        frappe.throw("Invalid secret", frappe.PermissionError)

    frappe.enqueue(process_update, update=frappe.request.get_json(), queue="short")


def link_code_key(code):
    return f"telegram_link:{code}"


def create_link_code(user):
    code = f"{secrets.randbelow(10**6):06d}"
    frappe.cache().set_value(link_code_key(code), user, expires_in_sec=LINK_CODE_TTL)
    return code


def fetch_bot_username():
    token = get_settings().get_password("telegram_bot_token")
    response = requests.get(f"{TELEGRAM_API}/bot{token}/getMe", timeout=10)
    response.raise_for_status()
    return response.json()["result"]["username"]


def get_bot_username():
    return frappe.cache().get_value("telegram_bot_username", generator=fetch_bot_username)


def link_account(chat_id, code):
    user = frappe.cache().get_value(link_code_key(code))
    if not user:
        return send_message(
            chat_id, "That code is invalid or has expired. Generate a new one on the Telegram page."
        )

    frappe.cache().delete_value(link_code_key(code))
    frappe.db.set_value("User", {"telegram_chat_id": str(chat_id)}, "telegram_chat_id", None)
    frappe.db.set_value("User", user, "telegram_chat_id", str(chat_id))
    send_message(chat_id, f"Linked to {get_fullname(user)}. Send me a voice note describing an expense.")


def process_update(update):
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    command, _, argument = message.get("text", "").partition(" ")
    if command in ("/link", "/start") and argument.strip():
        return link_account(chat_id, argument.strip())

    user = get_user_by_chat_id(chat_id)
    if not user:
        return send_message(
            chat_id,
            "This chat is not linked yet. Open the Telegram page in the app, "
            "generate a code and send it here as /link CODE.",
        )

    frappe.set_user(user)
    if "voice" in message:
        try:
            return handle_voice(chat_id, user, message["voice"])
        except Exception:
            frappe.log_error()
            return send_message(chat_id, "Could not process that voice note.")
    send_message(chat_id, "Send me a voice note describing your expense.")
