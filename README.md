# Expense Manager

A Frappe app for tracking personal and family expenses. Individuals manage categories, budgets and dependents, and log expenses by sending a Telegram voice note. Dependents get a simple portal for their pocket money and savings, with no Desk access.

## Features

**Individual**
- Create expense categories and set a monthly budget per category
- Get notified when a category goes over budget
- Send a Telegram voice note ("I spent 200 on Zomato") and receive a summary back
- Add dependents and allocate their monthly pocket money
- View weekly and monthly reports with charts for yourself and your dependents

**Dependent** (no Desk access)
- Record expenses and see how much pocket money is left this month
- Roll unused pocket money over to savings, manually or automatically at month end

## Tech stack

- **Backend:** Frappe Framework v15, Python
- **Frontend:** Vue 3, Vite, Tailwind CSS 3, Frappe UI (including its chart components)
- **Voice and extraction:** Telegram Bot API, Google Gemini API (audio transcription and expense extraction)
- **Scheduler:** Frappe scheduler for the monthly savings rollover

## How voice capture works

1. The bot receives a voice note through a Telegram webhook.
2. The webhook checks a shared secret and queues a background job, so Telegram gets an immediate response.
3. The job downloads the audio, transcribes it with Gemini, and extracts the amount, category and description as JSON, using your existing categories as the allowed values.
4. An Expense is created for the user linked to that Telegram chat, and the bot replies with a summary and the remaining budget.

## Roles and access

| Role | Desk access | What they can do |
| --- | --- | --- |
| Individual | Yes | Manage categories, budgets, dependents, pocket money; view reports |
| Dependent | No | Add expenses, view own balance, roll over to savings |

Record-level access is enforced with permission query conditions, so a dependent can only read their own records and an individual can only read their own and their dependents' records.

## Project structure

```
expense_manager/
├── api.py                  Whitelisted endpoints for the frontend
├── telegram.py             Webhook, transcription, extraction, replies
├── permissions.py          Ownership rules for each DocType
├── hooks.py                Scheduler, permissions, routing, home pages
├── expense_manager/doctype/
│   ├── expense_category/
│   ├── budget/
│   ├── expense/            Overspend check, shared expense creation
│   ├── dependent/          Pocket money balance and savings rollover
│   ├── pocket_money_allocation/
│   ├── savings_entry/
│   └── expense_manager_settings/   Telegram and Gemini credentials
└── www/expense-manager/    Page that serves the Vue app
frontend/                   Vue 3 + Vite + Frappe UI source
```

## Setup

### 1. Install the app

```bash
bench get-app https://github.com/thokalayashwanth1/expense-manager --branch develop
bench --site <your-site> install-app expense_manager
```

### 2. Build the frontend

```bash
cd apps/expense_manager/frontend
npm install --legacy-peer-deps
npm run build
```

### 3. Create roles and the Telegram field

- Create two Roles: `Individual` (Desk Access on) and `Dependent` (Desk Access off).
- Add a Data field named `telegram_chat_id` to the User DocType (Customize Form), marked unique.
- Give your own user the `Individual` role.

### 4. Configure credentials

Open **Expense Manager Settings** and fill in:

| Field | Value |
| --- | --- |
| `telegram_bot_token` | Token from @BotFather |
| `gemini_api_key` | Key from Google AI Studio |
| `webhook_secret` | Any random string of letters and numbers, for example `openssl rand -hex 16` |

Secrets are stored as Password fields and are never committed to the repository.

### 5. Connect the Telegram bot

Telegram needs a public HTTPS address. For local development use a tunnel such as ngrok:

```bash
ngrok http 8000
curl "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -d "url=<PUBLIC_URL>/api/method/expense_manager.telegram.webhook" \
  -d "secret_token=<WEBHOOK_SECRET>"
```

Then send the bot a message. It replies with your chat ID, which you save in the `telegram_chat_id` field of your user so the bot knows who you are.

### 6. Open the app

Visit `/expense-manager` on your site. Individuals see the dashboard, budgets and dependents pages. Dependents are sent to their portal.

## API

| Endpoint | Purpose |
| --- | --- |
| `expense_manager.api.get_profile` | Current user and whether they are a dependent |
| `expense_manager.api.get_expense_report` | Totals by person and category for a week or month |
| `expense_manager.api.get_budget_status` | This month's budgets with amount spent |
| `expense_manager.api.set_budget` | Create or update this month's budget for a category |
| `expense_manager.api.add_dependent` | Create a dependent and their login |
| `expense_manager.api.get_dependents` | Dependents with their pocket money balance |
| `expense_manager.api.set_pocket_money` | Set this month's allowance for a dependent |
| `expense_manager.api.add_expense` | Record an expense |
| `...dependent.get_pocket_money_balance` | Allocated, spent, saved and remaining amounts |
| `...dependent.roll_over_to_savings` | Move the remaining balance into savings |
| `expense_manager.telegram.webhook` | Telegram webhook (secret-protected) |

## Design notes

- No raw SQL: queries use `frappe.qb`, `frappe.get_list`, and `frappe.db.get_value`.
- Spend totals, expense creation, family lookups and the pocket money balance each live in one function, shared by the web app, the Telegram bot and the scheduler.
- The savings rollover is idempotent: once a month is rolled over the balance is zero, so a repeat call does nothing.
- The voice flow retries on temporary API failures (429, 500, 503) with backoff.
- Gemini is used for both transcription and extraction, so one API key covers the whole voice flow.

## Screenshots and demo

Screenshots and the demo video will be added here.

## License

MIT
