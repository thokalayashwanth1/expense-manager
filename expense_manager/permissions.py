import frappe


def get_family(user):
    return [user, *frappe.get_all("Dependent", filters={"parent_user": user}, pluck="user")]


def expense_query(user):
    if user == "Administrator":
        return ""
    family = ", ".join(frappe.db.escape(member) for member in get_family(user))
    return f"`tabExpense`.spent_by in ({family})"


def dependent_has_permission(doc, user=None, permission_type=None):
    return (user or frappe.session.user) in (doc.user, doc.parent_user)

def family_filter(table, column):
    def query(user):
        if user == "Administrator":
            return ""
        dependents = frappe.get_all(
            "Dependent",
            or_filters={"user": user, "parent_user": user},
            pluck="name",
        )
        names = ", ".join(frappe.db.escape(name) for name in dependents) or "''"
        return f"`tab{table}`.{column} in ({names})"

    return query


allocation_query = family_filter("Pocket Money Allocation", "dependent")
savings_query = family_filter("Savings Entry", "dependent")


def dependent_query(user):
    if user == "Administrator":
        return ""
    return (
        f"(`tabDependent`.user = {frappe.db.escape(user)} "
        f"or `tabDependent`.parent_user = {frappe.db.escape(user)})"
    )


def budget_query(user):
    if user == "Administrator":
        return ""
    return f"`tabBudget`.user = {frappe.db.escape(user)}"
