import frappe


def log_change(doc, method=None):

    if doc.doctype == "Audit":
        return

    new = frappe.new_doc("Audit")

    new.doctype_name = doc.doctype
    new.document_name = doc.name
    new.action = method
    new.user = frappe.session.user
    new.timestamp = frappe.utils.now()

    new.insert(ignore_permissions=True)