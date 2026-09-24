# Copyright (c) 2026, yogesh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class ClassSession(Document):

    def validate(self):

        # E1 - Session date validation
        if self.docstatus == 0 or self.is_new():
            if getdate(self.session_date) < getdate():
                frappe.throw(
                    "Session date cannot be in past for Draft record"
                )

        session_type = frappe.get_doc(
            "Session Type",
            self.session_type
        )

        for attendee in self.attendees:

            packages = frappe.get_doc(
                "Package Purchase",
                attendee.package_purchase
            )

            attendee.credits_charged = session_type.credits_required

            if packages.member != attendee.member:
                frappe.throw(
                    f"Error: Mismatched Package - {packages.name}"
                )

            if packages.status != "Active":
                frappe.throw(
                    f"Error: Package - {packages.name} is not Active"
                )

            if getdate(packages.expiry_date) < getdate(self.session_date):
                frappe.throw(
                    f"Error: Package - {packages.name} is expired"
                )

            if packages.credits_remaining < attendee.credits_charged:
                frappe.throw(
                    f"Insufficient credits for member - {attendee.member}. "
                    f"Remaining Credits - {packages.credits_remaining}"
                )


    def before_submit(self):

        # Session must be Completed
        if self.status != "Completed":
            frappe.throw(
                "Status must be completed before submitting!"
            )

        # No attendee can remain Booked
        for attendee in self.attendees:
            if attendee.attendance_status == "Booked":
                frappe.throw(
                    f"Attendee {attendee.member} cannot be Booked before submission"
                )

    def on_submit(self):

        no_show_forfeits_credit = frappe.db.get_single_value(
            "Studio Settings",
            "no_show_forfeits_credit"
        )

        threshold = frappe.db.get_single_value(
            "Studio Settings",
            "low_balance_alert_threshold"
        )

        for attendee in self.attendees:

            should_charge = (
                attendee.attendance_status == "Attended"
                or (
                    attendee.attendance_status == "No-Show"
                    and no_show_forfeits_credit
                )
            )

            if not should_charge:
                continue

            package = frappe.get_doc(
                "Package Purchase",
                attendee.package_purchase
            )

            credits = attendee.credits_charged

            new_credits_used = package.credits_used + credits
            new_credits_remaining = package.credits_remaining - credits

            new_status = (
                "Fully Used"
                if new_credits_remaining == 0
                else package.status
            )

            frappe.db.set_value(
                "Package Purchase",
                package.name,
                {
                    "credits_used": new_credits_used,
                    "credits_remaining": new_credits_remaining,
                    "status": new_status
                }
            )

            if new_credits_remaining <= threshold:
                frappe.enqueue(
                    "flexledger.api.send_low_balance_email",
                    member=package.member,
                    package_purchase=package.name,
                    credits_remaining=new_credits_remaining,
                    threshold = threshold
                )

    def on_cancel(self):
        self.status = "Cancelled"

        no_show_forfeits_credit = frappe.db.get_single_value(
            "Studio Settings",
            "no_show_forfeits_credit"
        )

        credits_reqd = frappe.db.get_value(
            "Session Type",
            self.session_type,
            "credits_required"
        )

        for attendee in self.attendees:

            should_charge = (
                attendee.attendance_status == "Attended"
                or (
                    attendee.attendance_status == "No-Show"
                    and no_show_forfeits_credit
                )
            )

            if not should_charge:
                continue

            package = frappe.get_doc(
                "Package Purchase",
                attendee.package_purchase
            )

            prev_used = package.credits_used

            package.credits_used = prev_used - credits_reqd
            package.credits_remaining = (
                package.total_credits - package.credits_used
            )

            if package.status == "Fully Used":
                package.status = "Active"

            package.save()
            
    def on_trash(self):
        if self.status not in ("Cancelled","Draft"):
            frappe.throw("Upcoming non-cancelled Sessions cannot be deleted!!!") 
            
    # def on_update(self):
    #     self.save()
    