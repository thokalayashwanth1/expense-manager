import frappe
from frappe.model.document import Document
from frappe.utils import add_months, getdate

from expense_manager.expense_manager.doctype.expense.expense import get_month_spend


class Dependent(Document):
    pass


def get_allocated(dependent, date):
    return frappe.db.get_value(
        "Pocket Money Allocation",
        {"dependent": dependent, "month": str(date.month), "year": date.year},
        "amount",
    ) or 0


@frappe.whitelist()
def get_pocket_money_balance(dependent, date=None):
    frappe.has_permission("Dependent", doc=dependent, throw=True)
    date = getdate(date)
    user = frappe.db.get_value("Dependent", dependent, "user")
    allocated = get_allocated(dependent, date)
    spent = get_month_spend(user, date)
    return {"allocated": allocated, "spent": spent, "balance": allocated - spent}




@frappe.whitelist()
def roll_over_to_savings(dependent, date=None):
    date = getdate(date)
    filters = {"dependent": dependent, "month": str(date.month), "year": date.year}
    balance = get_pocket_money_balance(dependent, date)["balance"]
    if balance <= 0 or frappe.db.exists("Savings Entry", filters):
        return 0

    frappe.get_doc({"doctype": "Savings Entry", **filters, "amount": balance}).insert(
        ignore_permissions=True
    )
    return balance


def roll_over_all():
    date = add_months(getdate(), -1)
    for dependent in frappe.get_all("Dependent", pluck="name"):
        roll_over_to_savings(dependent, date)