# Copyright (c) 2026, yogesh and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class PackagePurchase(Document):
	def validate(self):
		self.credits_remaining = self.total_credits - self.credits_used
