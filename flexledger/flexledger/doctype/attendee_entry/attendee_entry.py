# Copyright (c) 2026, yogesh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AttendeeEntry(Document):
    pass
	# def validate(self):
	# 	parent = frappe.get_doc("Session",self.parent)
	# 	pt_type = frappe.get_doc("Session Type",parent.session_type)
	# 	self.credits_charged = pt_type.credits_required


