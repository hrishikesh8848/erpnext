frappe.ui.form.on("Zero Budget", {
    onload: function(frm){
        frm.savecancel = function(btn, callback, on_error){ console.log("jiiri");return frm._cancel(btn, callback, on_error, false);}
    },
    project: function(frm) {
        if (frm.doc.project) {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Project",
                    fieldname: "company",
                    filters: {
                        name: frm.doc.project
                    }
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value("company", r.message.company);
                        frm.set_value("posting_date", frappe.datetime.get_today());
                        // frm.set_value("document_date", frappe.datetime.get_today());
                    }
                }
            });
        }
    },

    get_wbs: function(frm) {
        if (frm.doc.project) {
            frappe.call({
                method: "erpnext.accounts.doctype.zero_budget.zero_budget.work_breakdown_structure",
                args: {
                    project: frm.doc.project
                },
                callback: function(r) {
                    if (r.message) {
                        frm.clear_table("zero_budget_item");
                        
                        // Add rows to the child table
                        r.message.forEach(function(wbs) {
                            if (wbs.wbs_level == 1) {  // Corrected the closing parenthesis
                                let row = frm.add_child("zero_budget_item");
                                row.wbs_element = wbs.name;
                                row.wbs_name = wbs.wbs_name;
                                row.wbs_level = wbs.wbs_level;
                                row.zero_budget = wbs.zero_budget;
                            
                                frm.refresh_field("zero_budget_item"); // Refresh the field to reflect changes
                            }
                            
                            
                            
                        });

                        frm.refresh_field("zero_budget_item");
                    }
                }
            });
        }
    }
});



frappe.ui.form.on("Zero Budget Item", {
    zero_budget: function(frm,cdt,cdn) {
        var child = locals[cdt][cdn];
        let total_amount = 0;
        frm.doc.zero_budget_item.forEach(row => {
            total_amount += row.zero_budget;
        });
        console.log("1")
        frm.set_value("total",total_amount);
        frm.refresh_field("total");
    }
});