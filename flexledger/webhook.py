import frappe
import requests

frappe.utils.logger.set_log_level("INFO")
logger = frappe.logger("flexledger")

def send_webhook(session_name):
    import requests
    settings = frappe.get_single("Studio Settings")
    if not settings.webhook_url:
        return
    doc = frappe.get_doc("Class Session", session_name)
    payload = {"event": "session_completed", "session": doc.name, "attendees": len(doc.attendees)}
    try:
        r = requests.post(settings.webhook_url, json=payload, timeout=5)
        r.raise_for_status()
        logger.info(f"Response recieved : {r}")
        logger.info(f"Webhook sent successfully for the session {doc.name}")
    except Exception as e:
        frappe.log_error(f"Webhook failed: {e}", "Webhook Error")