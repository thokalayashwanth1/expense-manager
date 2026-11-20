import frappe
from frappe.query_builder.functions import Sum
from expense_manager.expense_manager.doctype.expense.expense import create_expense, get_month_spend
from expense_manager.expense_manager.doctype.dependent.dependent import get_pocket_money_balance
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

@frappe.whitelist()
def get_budget_status(date=None):
    date = getdate(date)
    user = frappe.session.user
    budgets = frappe.get_list(
        "Budget",
        filters={"user": user, "month": str(date.month), "year": date.year},
        fields=["name", "category", "amount"],
    )
    return [{**budget, "spent": get_month_spend(user, date, budget.category)} for budget in budgets]


@frappe.whitelist()
def set_budget(category, amount):
    date = getdate()
    filters = {
        "user": frappe.session.user,
        "category": category,
        "month": str(date.month),
        "year": date.year,
    }
    name = frappe.db.exists("Budget", filters)
    budget = frappe.get_doc("Budget", name) if name else frappe.new_doc("Budget")
    budget.update({**filters, "amount": amount})
    budget.save()
    return budget.name


@frappe.whitelist()
def get_dependents():
    dependents = frappe.get_list(
        "Dependent",
        filters={"parent_user": frappe.session.user},
        fields=["name", "dependent_name", "user"],
    )
    return [{**dependent, **get_pocket_money_balance(dependent.name)} for dependent in dependents]


@frappe.whitelist()
def set_pocket_money(dependent, amount):
    frappe.has_permission("Dependent", doc=dependent, throw=True)
    date = getdate()
    filters = {"dependent": dependent, "month": str(date.month), "year": date.year}
    name = frappe.db.exists("Pocket Money Allocation", filters)
    allocation = (
        frappe.get_doc("Pocket Money Allocation", name)
        if name
        else frappe.new_doc("Pocket Money Allocation")
    )
    allocation.update({**filters, "amount": amount})
    allocation.save(ignore_permissions=True)
    return allocation.name


@frappe.whitelist()
def add_expense(category, amount, description=None):
    return create_expense(frappe.session.user, category, amount, description, "Manual").name
