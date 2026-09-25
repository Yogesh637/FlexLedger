import frappe
from frappe.query_builder import DocType
from frappe.utils import add_days, getdate, today

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
        
@frappe.whitelist()
def unsafe_get_members():

    return frappe.db.get_all("Member", fields=["*"])


@frappe.whitelist()
def safe_get_members():

    fields = ["name", "member_name", "join_date", "status", "user", "phone", "email"]

    if "FIT Studio Manager" not in frappe.get_roles(frappe.session.user):
        fields.remove("phone")
        fields.remove("email")
    return frappe.get_list("Member", fields=fields)

def send_low_balance_email(member,package_purchase,credits_remaining,threshold):
    user = frappe.get_doc(
        "Member",
        member,
    )
    if not user.email:
        return
    frappe.sendmail(
        recipients=[user.email],
        subject = f"Low Credit Balance",
        message = f"""
                <h2>Low Credit Balance!!!<h2>
                
                <p> Dear {user.member_name} , Your Credits remaining for the package {package_purchase} is
                is lower than the required credits of the Gym , So kindly Purchase a new Package !!!
                </p>
                <p>Thank You</p>
                
                <p>Credits Remaining : {credits_remaining}</p>
                <p>Credits Required : {threshold}</p>
        """
    )
    
@frappe.whitelist()
def swap_trainer(session, reason):
    doc = frappe.get_doc("Class Session", session)

    trainer = frappe.db.get_value(
        "Trainer",
        {"status": "Active"},
        "name"
    )

    if not trainer:
        frappe.throw("No active trainer available.")

    doc.trainer = trainer
    doc.save()

    return {
        "success": True,
        "trainer": trainer,
        "reason": reason
    }
    
def check_expiring_packages():

    recent = frappe.db.get_value(
        "Audit Log",
        {"action": "expiry_check", "date": today()},
        "name",
    )

    if recent:
        return
    packages = frappe.get_all(
        "Package Purchase",
        filters={
            "status": "Active",
            "expiry_date": ["between", [today(), add_days(today(), 7)]],
        },
        fields=["name", "member", "expiry_date"],
    )
    
    for package in packages:
        frappe.db.set_value("Package Purchase", package.name, "status", "Active", update_modified=False)
    frappe.get_doc({
        "doctype": "Audit Log",
        "doctype_name": "Package Purchase",
        "document_name": "expiry_check",
        "action": "expiry_check",
        "user": "Administrator",
        "timestamp": frappe.utils.now_datetime(),
        "date": today(),
    }).insert(ignore_permissions=True)
    
    
    
# @frappe.whitelist()
# def get_member_balance(member_id):
