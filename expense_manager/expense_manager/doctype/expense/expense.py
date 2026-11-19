# Copyright (c) 2026, yashwanth and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.query_builder.functions import Sum
from frappe.utils import get_first_day, get_last_day, getdate


class Expense(Document):
    def after_insert(self):
        date = getdate(self.expense_date)
        budget = get_budget(self.spent_by, self.category, date)
        if not budget:
            return

        spent = get_month_spend(self.spent_by, self.category, date)
        if spent > budget:
            notify_overspend(self.spent_by, self.category, spent, budget)


def get_budget(user, category, date):
    return frappe.db.get_value(
        "Budget",
        {"user": user, "category": category, "month": str(date.month), "year": date.year},
        "amount",
    )


def get_month_spend(user, category, date):
    expense = frappe.qb.DocType("Expense")
    total = (
        frappe.qb.from_(expense)
        .select(Sum(expense.amount))
        .where(expense.spent_by == user)
        .where(expense.category == category)
        .where(expense.expense_date.between(get_first_day(date), get_last_day(date)))
    ).run()[0][0]
    return total or 0


def notify_overspend(user, category, spent, budget):
    frappe.get_doc(
        {
            "doctype": "Notification Log",
            "for_user": user,
            "type": "Alert",
            "subject": f"Over budget on {category}: spent {spent} of {budget}",
        }
    ).insert(ignore_permissions=True)