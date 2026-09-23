import frappe


def after_install():

    types = {
        "1:1 Personal Training": 2,
        "Group HIIT": 1,
        "Yoga Flow": 1
    }

    for session_type, credits in types.items():

        if not frappe.db.exists("Session Type", session_type):

            doc = frappe.new_doc("Session Type")
            doc.session_type_name = session_type
            doc.credits_required = credits
            doc.insert()

    if not frappe.db.exists("Studio Settings"):

        doc = frappe.new_doc("Studio Settings")
        doc.studio_name = "Studio Default"
        doc.manager_email = "yogesh@gmail.com"
        doc.default_cancellation_window_hours = 24
        doc.no_show_forfeits_credit = 1
        doc.low_balance_alert_threshold = 2
        doc.insert()

    frappe.msgprint("Default Records created Successfully!")