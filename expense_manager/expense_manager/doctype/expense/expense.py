import frappe
from frappe import _
from frappe.model.document import Document
from frappe.query_builder.functions import Sum
from frappe.utils import get_first_day, get_last_day, getdate, nowdate


class Expense(Document):
    def validate(self):
        if self.is_new() and self.category not in allowed_categories_for(self.spent_by):
            frappe.throw(_("{0} is not available for {1}").format(self.category, self.spent_by))

    def after_insert(self):
        date = getdate(self.expense_date)
        budget = get_budget(self.spent_by, self.category, date)
        if not budget:
            return

        spent = get_month_spend(self.spent_by, date, self.category)
        if spent > budget:
            notify_overspend(self.spent_by, self.category, spent, budget)


def get_blocked_categories(user):
    dependent = frappe.db.get_value("Dependent", {"user": user})
    if not dependent:
        return []
    return frappe.get_all(
        "Dependent Blocked Category",
        filters={"parent": dependent, "parenttype": "Dependent"},
        pluck="category",
    )


def allowed_categories_for(user):
    filters = {"enabled": 1}
    blocked = get_blocked_categories(user)
    if blocked:
        filters["name"] = ["not in", blocked]
    return frappe.get_all("Expense Category", filters=filters, pluck="name", order_by="name asc")


def get_budget(user, category, date):
    return frappe.db.get_value(
        "Budget",
        {"user": user, "category": category, "month": str(date.month), "year": date.year},
        "amount",
    )


def get_month_spend(user, date, category=None):
    expense = frappe.qb.DocType("Expense")
    query = (
        frappe.qb.from_(expense)
        .select(Sum(expense.amount))
        .where(expense.spent_by == user)
        .where(expense.expense_date.between(get_first_day(date), get_last_day(date)))
    )
    if category:
        query = query.where(expense.category == category)
    return query.run()[0][0] or 0


def notify_overspend(user, category, spent, budget):
    frappe.get_doc(
        {
            "doctype": "Notification Log",
            "for_user": user,
            "type": "Alert",
            "subject": f"Over budget on {category}: spent {spent} of {budget}",
        }
    ).insert(ignore_permissions=True)


def create_expense(user, category, amount, description, source):
    return frappe.get_doc(
        {
            "doctype": "Expense",
            "amount": amount,
            "category": category,
            "description": description,
            "expense_date": nowdate(),
            "spent_by": user,
            "source": source,
        }
    ).insert()
