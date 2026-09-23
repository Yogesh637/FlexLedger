frappe.ui.form.on("Class Session", {

    setup(frm) {
        frm.set_query("trainer", () => {
            return {
                filters: {
                    status: "Active",
                    specialization: frm.doc.session_type
                }
            };
        });
    },

    refresh(frm) {
        if (frm.doc.status === "Scheduled") {
            frm.dashboard.add_indicator("Scheduled", "blue");
        }
        else if (frm.doc.status === "Draft") {
            frm.dashboard.add_indicator("Draft", "yellow");
        }
        else if (frm.doc.status === "Completed") {
            frm.dashboard.add_indicator("Completed", "green");
        }
        else if (frm.doc.status === "Cancelled") {
            frm.dashboard.add_indicator("Cancelled", "red");
        }

        if (
            frm.doc.status === "Scheduled" &&
            frm.doc.session_date &&
            frappe.datetime.get_diff(
                frappe.datetime.get_today(),
                frm.doc.session_date
            ) >= 0
        ) {
            frm.add_custom_button("Finalize Session", () => {
                frm.set_value("status", "Completed");
                frm.save();
            });
        }

        frm.add_custom_button("Cancel Session", () => {

            let d = new frappe.ui.Dialog({
                title: "Cancellation Reason",

                fields: [
                    {
                        label: "Cancellation Reason",
                        fieldname: "cancellation_reason",
                        fieldtype: "Data",
                        reqd: 1
                    }
                ],

                size: "small",

                primary_action_label: "Submit",

                primary_action(values) {

                    frm.set_value("status", "Cancelled");
                    frm.set_value(
                        "cancellation_reason",
                        values.cancellation_reason
                    );

                    d.hide();
                }
            });

            d.show();
        }),
            frm.add_custom_button("Swap Trainer", () => {

                frappe.prompt(
                    {
                        label: "Reason",
                        fieldname: "reason",
                        fieldtype: "Data",
                        reqd: 1
                    },
                    (values) => {

                        frappe.confirm(
                            `Are you sure you want to swap the trainer?<br><br>
                                 Reason: ${values.reason}`,

                            () => {

                                frappe.call({
                                    method: "flexledger.api.swap_trainer",
                                    args: {
                                        session: frm.doc.name,
                                        reason: values.reason
                                    },

                                    callback: function (r) {
                                        frappe.msgprint("Trainer swapped successfully.");
                                        frm.trigger("trainer")
                                        frm.reload_doc();
                                    }
                                });

                            }
                        );

                    }
                );

            });
    }
});



frappe.ui.form.on("Attendee Entry", {
    member(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (!row.member) {
            return;
        }
        frappe.db.get_value(
            "Session Type",
            frm.doc.session_type,
            "credits_required"

        ).then(session => {

            const req_credits = session.message.credits_required;

            frappe.db.get_list(
                "Package Purchase",
                {
                    filters: {
                        member: row.member,
                        status: "Active"
                    },
                    fields: ["name", "credits_remaining"],
                    limit: 1
                }
            ).then(packages => {

                if (!packages.length) {
                    frappe.msgprint("No active package found.");

                    frappe.model.set_value(
                        cdt,
                        cdn,
                        "credits_remaining",
                        0
                    );

                    return;
                }

                const credits = packages[0].credits_remaining;

                frappe.model.set_value(
                    cdt,
                    cdn,
                    "credits_remaining",
                    credits
                );

                if (credits < req_credits) {
                    frappe.msgprint(
                        `Insufficient credits. Member has ${credits} credits, but this session requires ${req_credits}.`
                    );
                }

            });

        });

    }

});