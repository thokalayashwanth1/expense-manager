import frappe
from frappe.query_builder.functions import Sum
from expense_manager.permissions import get_family

from frappe.utils import (
    add_days,
    get_first_day,
    get_first_day_of_week,
    get_fullname,
    get_last_day,
    getdate,
)


def get_period_range(period, date):
    if period == "week":
        start = get_first_day_of_week(date)
        return start, add_days(start, 6)
    return get_first_day(date), get_last_day(date)


@frappe.whitelist()
def get_expense_report(period="month", date=None):
    start, end = get_period_range(period, getdate(date))
    
    expense = frappe.qb.DocType("Expense")
    return (
        frappe.qb.from_(expense)
        .select(expense.spent_by, expense.category, Sum(expense.amount).as_("total"))
        .where(expense.spent_by.isin(get_family(frappe.session.user)))
        .where(expense.expense_date.between(start, end))
        .groupby(expense.spent_by, expense.category)
    ).run(as_dict=True)



@frappe.whitelist()
def get_profile():
    user = frappe.session.user
    return {
        "user": user,
        "full_name": get_fullname(user),
        "dependent": frappe.db.get_value("Dependent", {"user": user}, "name"),
    }


@frappe.whitelist()
def add_dependent(full_name, email, password):
    frappe.only_for("Individual")
    user = frappe.get_doc(
        {
            "doctype": "User",
            "email": email,
            "first_name": full_name,
            "new_password": password,
            "send_welcome_email": 0,
            "roles": [{"role": "Dependent"}],
        }
    ).insert(ignore_permissions=True)
    return frappe.get_doc(
        {
            "doctype": "Dependent",
            "dependent_name": full_name,
            "user": user.name,
            "parent_user": frappe.session.user,
        }
    ).insert().name