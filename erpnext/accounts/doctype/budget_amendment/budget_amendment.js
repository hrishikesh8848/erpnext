// Budget Amendment
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
    refresh: function(frm) {
        frm.set_query("wbs_element", "budget_amendment_items", function () {
            return {
                filters: {
                    "project":frm.doc.project,
                    "docstatus": 1,
                    "wbs_level": ["!=", '0']
                },
            };
        });
    },
    onload: function(frm) {
        frm.set_query("project", function() {
            return {};
        });

        if (!frm.doc.posting_date) {
            frm.set_value("posting_date", frappe.datetime.get_today());
        }

        frm.savecancel = function(btn, callback, on_error){return frm._cancel(btn, callback, on_error, false);}
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
                    total_amount += row.increment_budget || 0;
                }
            });
            frm.set_value("total_increment_budget", total_amount);
            frm.refresh_field("total_increment_budget");
        }
    },

    decrement_budget: function(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        let total_amount = 0;
        
        if(child.increment_budget) {
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
                    total_amount += row.decrement_budget || 0; 
                }
            });
            frm.set_value("total_decrement_budget", total_amount);
            frm.refresh_field("total_decrement_budget");
        }
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
    },
    wbs_element: function(frm,cdt,cdn) {
        var child = locals[cdt][cdn];
        frappe.db.get_value("Work Breakdown Structure", child.wbs_element, ['wbs_name','wbs_level','overall_budget'])
        .then(response => {
            child.wbs_name = response.message.wbs_name || null;
            child.level = response.message.wbs_level || null;
            child.overall_budget = response.message.overall_budget || null;
            let row = frm.fields_dict['budget_amendment_items'].grid.get_row(cdn);
			row.refresh_field('wbs_name');
            row.refresh_field('level');
            row.refresh_field('overall_budget');
        });
    }
});
