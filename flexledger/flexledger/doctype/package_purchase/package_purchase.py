# Copyright (c) 2026, yogesh and contributors
# For license information, please see license.txt

from frappe.model.document import Document
import frappe

class PackagePurchase(Document):

    def validate(self):
        self.calc_credits()

    def calc_credits(self):
        self.credits_remaining = (
            self.total_credits - self.credits_used
        )
    def before_print(self,print_format = None , doc = None):
        
        self.print_summary = f"{self.member} - {self.total_credits} credits"
        