import frappe


def class_session_query(user):
    if user == "Administrator":
        return ""

    if "FIT Trainer" not in frappe.get_roles(user):
        return ""

    trainer = frappe.db.get_value(
        "Trainer",
        {"user": user},
        "name"
    )


    if not trainer:
        return "1 = 0"

    return f"`tabClass Session`.trainer = '{trainer}'"