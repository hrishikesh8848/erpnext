// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("WBS Budget", {
    onload: function(frm) {
        // Add custom button to fetch accounts
        frm.add_custom_button(__('Get GL Accounts'), function() {
            frm.events.get_gl_accounts(frm);
        }, __("Actions"));

        frm.savecancel = function(btn, callback, on_error){ console.log("jiiri");return frm._cancel(btn, callback, on_error, false);}
    },

    project(frm) {
        // Function to set filtered WBS options based on project
        frappe.call({
            method: "erpnext.accounts.doctype.zero_budget.zero_budget.work_breakdown_structure",
            args: {
                project: frm.doc.project
            },
            callback: function(r) {
                if (r.message) {    
                    let filtered_records = r.message.map(wbs => wbs.name);
                    console.log(filtered_records, ": Filtered records");

                    frm.set_query("wbs", () => {
                        return {
                            filters: {
                                name: ['in', filtered_records]
                            }
                        };
                    });
                }
            }
        });
    },

    get_gl_accounts: function(frm) {
        if (frm.doc.project && frm.doc.wbs) {
            frappe.call({
                method: "erpnext.accounts.doctype.wbs_budget.wbs_budget.get_gl_accounts",
                args: {
                    wbs: frm.doc.wbs
                },
                callback: function(r) {
                    if (r.message) {
                        frm.clear_table("accounts");
                        // Add new rows to accounts table
                        r.message.forEach(function(wbs) {
                            let row = frm.add_child("accounts");
                            row.child_wbs = wbs.name;
                            row.account = wbs.gl_account;
                        });

                        frm.refresh_field("accounts");
                    }
                }
            });
        }
    },
    wbs: function(frm) {
        frappe.db.get_value("Work Breakdown Structure",frm.doc.wbs, 'available_budget')
        .then(response => {
            let available_budget = response.message.available_budget;
            frm.set_value("available_budget",available_budget);
            frm.refresh_field("available_budget");
            console.log(response);
        });
    },
    from_date: function(frm) {
        update_budget_items(frm);
    },
    to_date: function(frm) {
        update_budget_items(frm);
    }
});

function update_budget_items(frm) {
    const fromDate = frm.doc.from_date ? new Date(frm.doc.from_date) : null;
    const toDate = frm.doc.to_date ? new Date(frm.doc.to_date) : null;

    if (fromDate && toDate) {
        let budgetItems = [];
        let currentDate = new Date(fromDate);

        while (currentDate <= toDate) {
            const month = currentDate.toLocaleString('default', { month: 'long' });
            const year = currentDate.getFullYear();
            budgetItems.push({ month: month, year: year });
            currentDate.setMonth(currentDate.getMonth() + 1);
        }

        frm.clear_table("wbs_budget_items");
        budgetItems.forEach(item => {
            const row = frm.add_child("wbs_budget_items");
            row.month = item.month;
            row.year = item.year;
        });
        frm.refresh_field("wbs_budget_items");
    }
}

frappe.ui.form.on("WBS Budget Items", {
    amount: function(frm,cdt,cdn) {
        calculate_total_amount(frm);
    },
    wbs_budget_items_remove: function(frm,cdt,cdn) {
        calculate_total_amount(frm);
    }
});

function calculate_total_amount(frm) {
    let total_amount = 0;
    frm.doc.wbs_budget_items.forEach(entry => {
        total_amount += parseFloat(entry.amount) || 0;
    });
    frm.set_value("total_amount",total_amount);
    frm.refresh_field("total_amount");
}
