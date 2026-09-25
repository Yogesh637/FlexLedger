1.`B2c — Dangerous Patterns`
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

2.`B2d — Concurrency, One Question`
`Question`-optimistic locking
In README_internals.md: two front-desk staff open the same Package Purchase at once and both try to save a change. Why would you see a "Document has been modified after you have opened it" error, and how does Frappe prevent one of them from silently overwriting the other's edit? (One paragraph.)

`Answer`
    "Document has been modified after you have opened it" is a expection raised by frappe's locking mechanism.

    When a same record is opened by two desk-staffs,frappe updates the document's timestamp while the first staff updates/modifies the document.so when the second staff would see a"Document has been modified after you have opened it" expection because of the timestamp mismatch.

###
3.`C3 — Attendee Entry & Package Purchase`
`Question`:
In README_internals.md: rename a test Member record. Does member on linked Package Purchase records update automatically? Why or why not?

`Answer`:
    Yes.If a member record is renamed,then all the linked Package Purchase records records the update automatically,Because if the linked docs doesn't update automatically ,then the system consistency will be broken and requires dev to manually finf the linked docs and update it.

###

4.`D2 — Row-Level Filtering & Data Leaks`
`Question` - get_list vs get_all
README_internals.md: why is frappe.get_all dangerous in a whitelisted method exposed to low-privilege users?

`Answer`:
    frappe.get_all is a dangerous because it bypasses permission filtering,thus even low-privilage users without read,write permission can easily fetch data using the whitelisted API.

    While frappe.get_list supports permission filtering and doesn't fetch records if the frappe.session.user doesn't have enough permissions.

###

5.`E1 — Complete Lifecycle`
`Question`-on_update() — the recursion pitfall
Call self.save() inside on_update and observe what breaks. Explain it and correct the pattern in README_internals.md

`Answer`:
    Using self.save() in on_update() results in a recursion error because the save() event itself triggers on_update() internally,thus causing a never ending loop.

###

6.`E2 — autoname & Renaming`
`Question`:
Implement autoname() on Package Purchase so its name embeds the member's short code plus a running sequence. Call frappe.rename_doc("Member", old, new, merge=False) in a utility function and show linked fields update automatically. `Explain when merge=True would be dangerous.`

`Answer`:
    merge = true is considered to be dangerous when we want both the old and new records,because wit hmerge = true ,the old record will be overrided by the new record and may cause inconsistency in linked documents at some cases.
###

7.`I1 — Query Report: Members Running Low`
`Question`:
Selects name, member, credits_remaining, expiry_date, status from Package Purchase. Filter: status = "Active" AND credits_remaining <= %(threshold)s. In README_internals.md: show the f-string version side by side with the parameterized version, and explain why the latter is always preferred.

`Answer`:

    1.F-string :

    threshold = frappe.db.get_single_value(
    "Studio Settings",
    "low_balance_alert_threshold"
        )

    query = f"""
        SELECT name, member, credits_remaining
        FROM `tabPackage Purchase`
        WHERE credits_remaining <= {threshold}
    """

    data = frappe.db.sql(query, as_dict=True)

    2.Parameterized :

    threshold = frappe.db.get_single_value(
    "Studio Settings",
    "low_balance_alert_threshold"
    )

    query = """
        SELECT name, member, credits_remaining
        FROM `tabPackage Purchase`
        WHERE credits_remaining <= %(threshold)s
    """

    data = frappe.db.sql(
        query,
        {"threshold": threshold},
        as_dict=True
    )


   `Explanation`:
        The parameterized version treats the passesd value as a single string so it will block sql injections,but in f-string version if a injection sql code is passed in query then the injected sql will be exceuted with query causiing data loss and security issues.so the second vercsion is always preferrable.

###

8.`H1 — Class Session Form Script`
`Question`- H1 — Class Session Form Script
In README_internals.md: why does a frappe.call inside the validate client event not work, and why must async fetches happen in onload/refresh instead?.

`Answer`:
    frappe.call() will not work in validate() because validate() is synchrounous and doesnot wait for the results fetched via frappe.call(),so if a validation is done based on results from frappe.call() then it will cause error ,because validation will be done before the result is fetched.

    So frappe.call() should be written onload() or refresh() ,so the result can be fetched before the document is saved and validated.

###

9.`N1 — ignore_permissions Audit & JS-Hiding Pitfall`
`Question`:
Explain in README_internals.md why hiding a field in JavaScript is not a security measure.

`Answer`:
    Hiding a field in JS is not a security measure because it is effective only in desk and runs only in local machine,and users can still fetch the field using API methods and it has zero security in runtime environment,so it is always recommended to add security measures,validations in server side where it is impossible to bypass the validations and security.

###

10.`J1 — Package Receipt`
`Question`:
In README_internals.md: explain the difference between putting a frappe.get_all() call directly inside the Jinja template versus pre-computing in before_print() and referencing doc.precomputed_field.

`Answer`:
    Putting a frappe.get_all() directly inside Jinja template will mix the printing format logic and the data computing logix together ,which make the code hareder to maintain and difficult to understand,While precomputing in before_print() seorates the data computation logic and the print format logic makeing the code easier to maintain and debugging.