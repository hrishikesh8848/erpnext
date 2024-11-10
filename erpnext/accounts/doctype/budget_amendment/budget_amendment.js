frappe.ui.form.on("Budget Amendment", {
    project: function(frm) {
        if (frm.doc.project) {
            frappe.db.get_value("Project", frm.doc.project, ["project_name", "company"], (r) => {
                if (r) {
                    frm.set_value("project_name", r.project_name);
                    frm.set_value("company", r.company);
                }
            });
        } else {
            frm.set_value("project_name", null);
            frm.set_value("company", null);
        }
    },

    onload: function(frm) {
        frm.set_query("project", function() {
            return {};
        });

        // if (!frm.doc.document_date) {
        //     frm.set_value("document_date", frappe.datetime.get_today());
        // }
        if (!frm.doc.posting_date) {
            frm.set_value("posting_date", frappe.datetime.get_today());
        }

        frm.savecancel = function(btn, callback, on_error){ console.log("jiiri");return frm._cancel(btn, callback, on_error, false);}
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
                        frm.clear_table("budget_amendment_items");
                        
                        // Add rows to the child table
                        r.message.forEach(function(wbs) {
                            let row = frm.add_child("budget_amendment_items");
                            row.wbs_element = wbs.name;
                            row.wbs_name = wbs.wbs_name;
                            row.level = wbs.wbs_level;
                            row.overall_budget = wbs.overall_budget;
                        });

                        frm.refresh_field("budget_amendment_items");
                    }
                }
            });
        }
    },

    
    
});

frappe.ui.form.on("Budget Amendment Items", {
    overall_budget: function(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        let total_amount = 0;

        if (frm.doc.budget_amendment_items && frm.doc.budget_amendment_items.length) {
            frm.doc.budget_amendment_items.forEach(row => {
                if (row.overall_budget !== undefined) {
                    total_amount += row.overall_budget || 0;
                }
            });
            console.log("Total Overall Budget:", total_amount);
            frm.set_value("total_overall_budget", total_amount);
            frm.refresh_field("total_overall_budget");
        } else {
            console.log("No budget amendment items found.");
        }
    },

    increment_budget: function(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        let total_amount = 0;
        
        if(child.decrement_budget) {
            child.increment_budget = 0
            frappe.msgprint(__("Please set decrement budget to 0"))
            child.total = child.overall_budget + child.increment_budget - child.decrement_budget
        } else {
            child.total = child.overall_budget + child.increment_budget
        }

        let row = frm.fields_dict['budget_amendment_items'].grid.get_row(cdn);
        row.refresh_field('increment_budget')
		row.refresh_field('total')

        // Check if budget_amendment_items is populated
        if (frm.doc.budget_amendment_items && frm.doc.budget_amendment_items.length) {
            frm.doc.budget_amendment_items.forEach(row => {
                if (row.increment_budget !== undefined) {
                    total_amount += row.increment_budget || 0; // Ensure we handle undefined values
                }
            });
            console.log("Total Increment Budget:", total_amount); // Debugging
            frm.set_value("total_increment_budget", total_amount);
            frm.refresh_field("total_increment_budget");
        } else {
            console.log("No budget amendment items found.");
        }

        // cur_frm.fields_dict["budget_amendment_items"].grid.grid_rows_by_docname[child.name].set_field_property('decrement_budget','read_only',1);

    },

    decrement_budget: function(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        let total_amount = 0;
        
        if(child.increment_budget) {
            console.log("Yes")
            child.decrement_budget = 0
            frappe.msgprint(__("Please set increment budget to 0"))
            child.total = child.overall_budget - child.decrement_budget + child.increment_budget
        } else {
            child.total = child.overall_budget - child.decrement_budget
        }
        let row = frm.fields_dict['budget_amendment_items'].grid.get_row(cdn);
        row.refresh_field('decrement_budget')
		row.refresh_field('total')
        

        // Check if budget_amendment_items is populated
        if (frm.doc.budget_amendment_items && frm.doc.budget_amendment_items.length) {
            frm.doc.budget_amendment_items.forEach(row => {
                if (row.decrement_budget !== undefined) {
                    total_amount += row.decrement_budget || 0; // Ensure we handle undefined values
                }
            });
            console.log("Total Decrement Budget:", total_amount); // Debugging
            frm.set_value("total_decrement_budget", total_amount);
            frm.refresh_field("total_decrement_budget");
        } else {
            console.log("No budget amendment items found.");
        }

        // cur_frm.fields_dict["budget_amendment_items"].grid.grid_rows_by_docname[child.name].set_field_property('increment_budget','read_only',1);
    },
    budget_amendment_items_remove: function(frm,cdt,cdn) {
        if (frm.doc.budget_amendment_items) {
            let total_increment_budget = 0;
            let total_decrement_budget = 0;
            frm.doc.budget_amendment_items.forEach(row => {
                total_increment_budget += row.increment_budget || 0;
                total_decrement_budget += row.decrement_budget || 0;
            });
            frm.set_value("total_increment_budget",total_increment_budget);
            frm.set_value("total_decrement_budget",total_decrement_budget);
            frm.refresh_field("total_increment_budget");
            frm.refresh_field("total_decrement_budget");
        }
    }
});

// frappe.ui.form.on('Budget Amendment Items', {
//     increment_budget: function(frm, cdt, cdn) {
//         let child = locals[cdt][cdn];
//         // Set rate to readonly if item_code is entered first for this row
//         frappe.model.set_value(cdt, cdn, 'decrement_budget', child.decrement_budget);
//         frappe.model.set_value(cdt, cdn, 'is_increment_budget_selected', 1);  // Track selection order
//         frm.fields_dict['budget_amendment_items'].grid.grid_rows_by_docname[cdn].toggle_editable('decrement_budget', false);
//         frm.refresh_field('budget_amendment_items');
//     },
//     decrement_budget: function(frm, cdt, cdn) {
//         let child = locals[cdt][cdn];
//         // Set item_code to readonly if rate is entered first for this row
//         frappe.model.set_value(cdt, cdn, 'increment_budget', child.increment_budget);
//         frappe.model.set_value(cdt, cdn, 'is_decrement_budget_selected', 1);  // Track selection order
//         frm.fields_dict['budget_amendment_items'].grid.grid_rows_by_docname[cdn].toggle_editable('increment_budget', false);
//         frm.refresh_field('budget_amendment_items');
//     },
//     budget_amendment_items_add: function(frm, cdt, cdn) {
//         let new_child = locals[cdt][cdn];
//         // Enable both fields only for the new row, keeping previous rows unaffected
//         frm.fields_dict['budget_amendment_items'].grid.grid_rows_by_docname[new_child.name].toggle_editable('increment_budget', true);
//         frm.fields_dict['budget_amendment_items'].grid.grid_rows_by_docname[new_child.name].toggle_editable('decrement_budget', true);
//         frm.refresh_field('budget_amendment_items');
//     }
// });


