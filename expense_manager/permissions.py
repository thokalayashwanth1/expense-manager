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