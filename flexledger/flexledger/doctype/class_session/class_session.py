# Copyright (c) 2026, yogesh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ClassSession(Document):

    def validate(self):
        class_session_type = frappe.get_doc("ClassSession Type", self.class_session_type)

        for attendee in self.attendees:
            attendee.credits_charged = class_session_type.credits_required