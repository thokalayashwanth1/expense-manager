import frappe
from frappe.model.document import Document
from frappe.utils import add_months, getdate

from expense_manager.expense_manager.doctype.expense.expense import get_month_spend


class Dependent(Document):
    pass


def get_month_amount(doctype, dependent, date):
    return (
        frappe.db.get_value(
            doctype,
            {"dependent": dependent, "month": str(date.month), "year": date.year},
            "amount",
        )
        or 0
    )


@frappe.whitelist()
def get_pocket_money_balance(dependent, date=None):
    frappe.has_permission("Dependent", doc=dependent, throw=True)
    date = getdate(date)
    user = frappe.db.get_value("Dependent", dependent, "user")
    allocated = get_month_amount("Pocket Money Allocation", dependent, date)
    spent = get_month_spend(user, date)
    saved = get_month_amount("Savings Entry", dependent, date)
    return {
        "allocated": allocated,
        "spent": spent,
        "saved": saved,
        "balance": allocated - spent - saved,
        "total_savings": sum(
            frappe.get_all("Savings Entry", filters={"dependent": dependent}, pluck="amount")
        ),
    }


@frappe.whitelist()
def roll_over_to_savings(dependent, date=None):
    date = getdate(date)
    balance = get_pocket_money_balance(dependent, date)["balance"]
    if balance <= 0:
        return 0

    frappe.get_doc(
        {
            "doctype": "Savings Entry",
            "dependent": dependent,
            "month": str(date.month),
            "year": date.year,
            "amount": balance,
        }
    ).insert(ignore_permissions=True)
    return balance


def roll_over_all():
    date = add_months(getdate(), -1)
    for dependent in frappe.get_all("Dependent", pluck="name"):
        roll_over_to_savings(dependent, date)
