import random

import frappe
from frappe.tests.classes.integration_test_case import IntegrationTestCase
from frappe.utils import add_days, today


class IntegrationTestClassSession(IntegrationTestCase):

    def create_test_data(self):
        # Generate unique values to avoid duplicate records between tests
        suffix = frappe.generate_hash(length=8)
        phone = f"9{random.randint(100000000, 999999999)}"

        # 1. Create Session Type
        session_type = frappe.get_doc({
            "doctype": "Session Type",
            "session_type_name": f"Test Session {suffix}",
            "credits_required": 2,
        }).insert(ignore_permissions=True)

        # 2. Create Trainer
        trainer = frappe.get_doc({
            "doctype": "Trainer",
            "trainer_name": f"Test Trainer {suffix}",
            "specialization": session_type.name,
        }).insert(ignore_permissions=True)

        # 3. Create Member
        member = frappe.get_doc({
            "doctype": "Member",
            "member_name": f"Test Member {suffix}",
            "phone": phone,
        }).insert(ignore_permissions=True)

        # 4. Create Package Purchase
        package = frappe.get_doc({
            "doctype": "Package Purchase",
            "member": member.name,
            "total_credits": 10,
            "credits_used": 0,
            "credits_remaining": 10,
            "amount_paid": 1000,
            "expiry_date": add_days(today(), 30),
            "status": "Active",
        }).insert(ignore_permissions=True)

        # 5. Create Class Session
        session = frappe.get_doc({
            "doctype": "Class Session",
            "session_type": session_type.name,
            "trainer": trainer.name,
            "session_date": add_days(today(), 1),
            "start_time": "10:00:00",
        })

        session.append("attendees", {
            "member": member.name,
            "package_purchase": package.name,
        })

        return {
            "session_type": session_type,
            "trainer": trainer,
            "member": member,
            "package": package,
            "session": session,
        }

    # --------------------------------------------------
    # TEST 1: Past date should be rejected
    # --------------------------------------------------
    def test_past_date_is_rejected(self):
        data = self.create_test_data()
        session = data["session"]

        session.session_date = add_days(today(), -1)

        with self.assertRaises(frappe.ValidationError):
            session.insert(ignore_permissions=True)

    # --------------------------------------------------
    # TEST 2: Future date should be allowed
    # --------------------------------------------------
    def test_future_date_is_allowed(self):
        data = self.create_test_data()
        session = data["session"]

        session.insert(ignore_permissions=True)

        self.assertTrue(session.name)

    # --------------------------------------------------
    # TEST 3: Package-member mismatch should be rejected
    # --------------------------------------------------
    def test_package_member_mismatch_is_rejected(self):
        data = self.create_test_data()
        session = data["session"]

        suffix = frappe.generate_hash(length=8)

        other_member = frappe.get_doc({
            "doctype": "Member",
            "member_name": f"Other Member {suffix}",
            "phone": f"9{random.randint(100000000, 999999999)}",
        }).insert(ignore_permissions=True)

        session.attendees[0].member = other_member.name

        with self.assertRaises(frappe.ValidationError):
            session.insert(ignore_permissions=True)

    # --------------------------------------------------
    # TEST 4: Attended session should deduct credits
    # --------------------------------------------------
    def test_attended_session_deducts_credits(self):
        data = self.create_test_data()
        session = data["session"]
        package = data["package"]

        session.status = "Completed"
        session.attendees[0].attendance_status = "Attended"

        session.insert(ignore_permissions=True)
        session.submit()

        updated_package = frappe.get_doc(
            "Package Purchase", package.name
        )

        self.assertEqual(updated_package.credits_used, 2)
        self.assertEqual(updated_package.credits_remaining, 8)

    # --------------------------------------------------
    # TEST 5: Cancelling a session should restore credits
    # --------------------------------------------------
    def test_cancelled_session_restores_credits(self):
        data = self.create_test_data()
        session = data["session"]
        package = data["package"]

        session.status = "Completed"
        session.attendees[0].attendance_status = "Attended"

        session.insert(ignore_permissions=True)
        session.submit()

        # Verify deduction
        updated_package = frappe.get_doc(
            "Package Purchase", package.name
        )

        self.assertEqual(updated_package.credits_used, 2)
        self.assertEqual(updated_package.credits_remaining, 8)

        # Cancel session
        session.cancel()

        # Verify credit restoration
        updated_package = frappe.get_doc(
            "Package Purchase", package.name
        )

        self.assertEqual(updated_package.credits_used, 0)
        self.assertEqual(updated_package.credits_remaining, 10)