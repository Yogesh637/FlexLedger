// Copyright (c) 2026, yogesh and contributors
// For license information, please see license.txt

frappe.ui.form.on("Trainer", {
	refresh(frm) {
        frm.add_custom_button("Add Email",()=>{
            let d = new frappe.ui.Dialog({
                title:"Email",
                fields:[{
                    label:"Email", 
                    fieldname:"get_email",
                    fieldtype:"Data"
                }],
                size:"small",
                primary_action_label:"Confirm Email",
                primary_action(values){
                    frm.doc.email = values.get_email
                    d.hide()
                }
            })
            d.show()
        })
	},
});
