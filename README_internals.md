`B2c — Dangerous Patterns`
`Question`:The snippet below has two bugs related to document lifecycle. Identify both and write the corrected version in README_internals.md.
def validate(self):
    self.total_charged = sum(r.credits_charged for r in self.attendees)
    self.save()
    pkg = frappe.get_doc("Package Purchase", self.package_purchase)
    pkg.credits_used += self.total_charged
    pkg.save()

`Answer`:
    Correct Code :
        def validate(self):
            self.total_charged = sum(r.credits_charged for r in self.attendees)

    1.Document lifecycle bug #1 - We should not use self.save() in validate(),because save() event internally trigger validate().Thus causing a never ending loop aka Recursive Error.

    2.Document lifecycle bug #2 - Updating pkg.credits_used inside validate() is wrong because validate() event is triggered internally in other events lifecycle also (ex: validate() happens in save()).so credits can be updated wrongly,thus it should be written in on_submit().

    3.Logical Bug - Total credits should not be used to calculate credits_used in a single package,because total credits include credits of more than one attendee.

    4.Logical Error - self.package_purchase is invalid , because package_purchase field is locateed in the child table (Attendee) not in parent doctype(Class Session).

###

`B2d — Concurrency, One Question`
`Question`-optimistic locking
In README_internals.md: two front-desk staff open the same Package Purchase at once and both try to save a change. Why would you see a "Document has been modified after you have opened it" error, and how does Frappe prevent one of them from silently overwriting the other's edit? (One paragraph.)

`Answer`
    "Document has been modified after you have opened it" is a expection raised by frappe's locking mechanism.

    When a same record is opened by two desk-staffs,frappe updates the document's timestamp while the first staff updates/modifies the document.so when the second staff would see a"Document has been modified after you have opened it" expection because of the timestamp mismatch.

###

`D2 — Row-Level Filtering & Data Leaks`
`Question` - get_list vs get_all
README_internals.md: why is frappe.get_all dangerous in a whitelisted method exposed to low-privilege users?

`Answer`:
    frappe.get_all is a dangerous because it bypasses permission filtering,thus even low-privilage users without read,write permission can easily fetch data using the whitelisted API.

    While frappe.get_list supports permission filtering and doesn't fetch records if the frappe.session.user doesn't have enough permissions.

###

`E1 — Complete Lifecycle`
`Question`-on_update() — the recursion pitfall
Call self.save() inside on_update and observe what breaks. Explain it and correct the pattern in README_internals.md

`Answer`:
    Using self.save() in on_update() results in a recursion error because the save() event itself triggers on_update() internally,thus causing a never ending loop.

###

`H1 — Class Session Form Script`
`Question`- H1 — Class Session Form Script
In README_internals.md: why does a frappe.call inside the validate client event not work, and why must async fetches happen in onload/refresh instead?.

`Answer`:
    frappe.call() will not work in validate() because validate() is synchrounous and doesnot wait for the results fetched via frappe.call(),so if a validation is done based on results from frappe.call() then it will cause error ,because validation will be done before the result is fetched.

    So frappe.call() should be written onload() or refresh() ,so the result can be fetched before the document is saved and validated.

###
