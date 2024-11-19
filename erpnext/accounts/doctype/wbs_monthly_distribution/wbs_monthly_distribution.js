// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
// WBS Monthly Distribution

frappe.ui.form.on("WBS Monthly Distribution", {
	refresh(frm) {
        update_available_budget(frm)
        add_default_distribution(frm)
        update_budget_in_distribution(frm)
        update_wbs_budget(frm)
        frm.set_query("for_wbs", () => {
            return {
                filters: {
                    is_group: 0,
                }
            }
        });
	},
    for_wbs(frm){
        update_available_budget(frm)
        // add_default_distribution(frm)
        update_budget_in_distribution(frm)
    },
});

function update_available_budget(frm){
    if(frm.doc.for_wbs){
        frappe.db.get_value("Work Breakdown Structure", frm.doc.for_wbs, "available_budget", (r) => {
            var current_available_budget = r.available_budget;
            frm.set_value("wbs_available_budget",current_available_budget );
            add_default_distribution(frm)
            update_budget_in_distribution(frm)
            
        });
    }
}

function add_default_distribution(frm){
    console.log(frm.doc.monthly_distribution)
    if(frm.is_new() && frm.doc.monthly_distribution && frm.doc.monthly_distribution.length == 0){
        console.log("99999")
        // List of months
    const months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ];
    const equal_percentage = 100 / 12;

    

    // Clear child table if it already has entries
    frm.clear_table("monthly_distribution");

    // Add each month with the equal percentage
    months.forEach(month => {
        const row = frm.add_child("monthly_distribution");
        row.month = month;
        row.allocation = equal_percentage;
        
        
    });

    // Refresh the child table to display added rows
    frm.refresh_field("monthly_distribution");
    }
    
}

function update_budget_in_distribution(frm) {
    

    frm.doc.monthly_distribution.forEach(row => {
        if (row.allocation && frm.doc.wbs_available_budget){
            row.budget = frm.doc.wbs_available_budget * (row.allocation / 100);
        }
        else{
            row.budget = 0.0
        }
    });

    frm.refresh_field("monthly_distribution");
}

function update_wbs_budget(frm){
    frm.add_custom_button(__('Update Budget'), function() {
        update_available_budget(frm)
        update_budget_in_distribution(frm)
    })
}

frappe.ui.form.on("Distribution Percentage", {
    allocation:function(frm,cdt,cdn){

        var child = locals[cdt][cdn]
        child.budget =  frm.doc.wbs_available_budget * (child.allocation / 100);
        frm.refresh_field("monthly_distribution");

    }
})

