import frappe
from frappe.query_builder.functions import Sum
from expense_manager.permissions import get_family

from frappe.utils import (
    add_days,
    get_first_day,
    get_first_day_of_week,
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