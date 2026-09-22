import frappe
from frappe.query_builder import DocType

@frappe.whitelist()
def get_low_balance_members():
    threshold = frappe.db.get_single_value(
        "Studio Settings",
        "low_balance_alert_threshold"
    )

    PP = DocType("Package Purchase")

    result = (
        frappe.qb.from_(PP)
        .select(
            PP.name,
            PP.member,
            PP.credits_remaining,
            PP.expiry_date
        )
        .where(
            (PP.credits_remaining <= threshold)
            & (PP.status == "Active")
        )
    ).run(as_dict=True)

    return result

@frappe.whitelist()
def transfer_package(package_name, new_member):
    try:
        result = frappe.db.sql(
            f"""
            UPDATE  `tabPackage Purchase`
            SET member = %s
            WHERE name = %s AND credits_used = 0
            """
            ,(new_member,package_name)            
        )
        frappe.db.commit()
        
        return {
            "success"
        }
        
    except:
        frappe.db.rollback()
        
        frappe.log_error(
            title = "Error while transfer package to new member",
            message = frappe.get_traceback()
        )