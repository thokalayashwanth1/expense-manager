import frappe

PASSWORD = "Zebra-Quartz-82-Maple"


def make_user(email, role):
    if not frappe.db.exists("User", email):
        user = frappe.get_doc(
            {"doctype": "User", "email": email, "first_name": email.split("@")[0], "send_welcome_email": 0}
        ).insert()
        user.add_roles(role)
    return email


def make_category(name):
    if not frappe.db.exists("Expense Category", name):
        frappe.get_doc({"doctype": "Expense Category", "category_name": name, "enabled": 1}).insert()
    return name


def make_dependent(email, parent):
    make_user(email, "Dependent")
    return frappe.get_doc(
        {"doctype": "Dependent", "dependent_name": email.split("@")[0], "user": email, "parent_user": parent}
    ).insert().name
