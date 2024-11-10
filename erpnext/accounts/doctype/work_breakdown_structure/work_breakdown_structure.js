frappe.ui.form.on("Work Breakdown Structure", {
    is_group: function(frm) {
        toggle_gl_account(frm);
        // toggle_gl_account(frm);
    },
    onload_post_render: function(frm) {
        toggle_gl_account(frm);
    },
    onload: function(frm) {
        frm.set_query("project", function() {
            return {
                filters: { "is_wbs": 1 }
            };
        });

        frm.set_query("parent_work_breakdown_structure", function() {
            return {
                filters: { 
                    "is_group": 1,
                    "docstatus": 1
                 }
            };
        });

        // Trigger budget calculations on form load
        // calculate_assigned_budget(frm);
        // calculate_available_budget(frm);
    },

    project: function(frm) {
        if (frm.doc.project) {
            frappe.db.get_value("Project", frm.doc.project, ["project_type", "project_name", "company"], (r) => {
                if (r) {
                    frm.set_value("project_type", r.project_type);
                    frm.set_value("project_name", r.project_name);
                    frm.set_value("company", r.company);
                }
            });
        } else {
            frm.set_value("project_type", null);
            frm.set_value("project_name", null);
            frm.set_value("company", null);
        }
    },

    parent_work_breakdown_structure: function(frm) {
        set_wbs_level(frm);
    },

    committed_overall_budget: function(frm) {
        calculate_assigned_budget(frm);
        calculate_available_budget(frm);
    },

    actual_overall_budget: function(frm) {
        calculate_assigned_budget(frm);
        calculate_available_budget(frm);
    },

    overall_budget: function(frm) {
        calculate_available_budget(frm);
    },

    refresh: function(frm) {
        // if (frm.is_new())
        // calculate_assigned_budget(frm);
        // calculate_available_budget(frm);

        // if (frm.doc.docstatus === 1 && !frm.fields_dict.allow_on_submit) {
        //     frm.save_or_update();
        // }

        frm.add_custom_button(__('Create Document'), function() {
            var dialog = new frappe.ui.Dialog({
                title: __('Create New Document'),
                fields: [
                    { fieldtype: 'Button', label: __('Material Request'), fieldname: 'material_request' },
                    { fieldtype: 'Button', label: __('Purchase Order'), fieldname: 'purchase_order' },
                    { fieldtype: 'Button', label: __('Purchase Invoice'), fieldname: 'purchase_invoice' }
                ]
            });

            dialog.fields_dict.material_request.$input.on('click', function() {
                dialog.hide();
                frappe.new_doc('Material Request', {
                    custom_project: frm.doc.project,
                    custom_project_name: frm.doc.project_name,
                    custom_work_breakdown_structure: frm.doc.name,
                    custom_wbs_name: frm.doc.wbs_name
                });
            });

            dialog.fields_dict.purchase_order.$input.on('click', function() {
                dialog.hide();
                frappe.new_doc('Purchase Order', {
                    custom_project: frm.doc.project,
                    custom_project_name: frm.doc.project_name,
                    custom_work_breakdown_structure: frm.doc.name,
                    custom_wbs_name: frm.doc.wbs_name
                });
            });

            dialog.fields_dict.purchase_invoice.$input.on('click', function() {
                dialog.hide();
                frappe.new_doc('Purchase Invoice', {
                    custom_project: frm.doc.project,
                    custom_project_name: frm.doc.project_name,
                    custom_work_breakdown_structure: frm.doc.name,
                    custom_wbs_name: frm.doc.wbs_name
                });
            });

            dialog.show();
        });
    }
});

function set_wbs_level(frm) {
    let parent = frm.doc.parent_work_breakdown_structure;
    if (parent) {
        frappe.db.get_value("Work Breakdown Structure", parent, "wbs_level")
        .then(response => {
            console.log(response)
            if (response.message && response.message.wbs_level) {
                let wbsLevel = parseInt(response.message.wbs_level, 10);
                frm.set_value("wbs_level", wbsLevel+1);
            }
        });
    }
}

// // Helper functions for setting WBS level and calculating budgets
// function set_wbs_level(frm) {
//     let parent = frm.doc.parent_work_breakdown_structure;
//     if (parent) {
//         frappe.db.get_value("Work Breakdown Structure", parent, ["is_group", "parent_work_breakdown_structure"], (r) => {
//             let level = r.is_group ? 2 : 1;
//             increment_level(frm, r.parent_work_breakdown_structure, level);
//         });
//     } else {
//         frm.set_value("wbs_level", 1);
//     }
// }

// function increment_level(frm, parent, current_level) {
//     if (parent) {
//         frappe.db.get_value("Work Breakdown Structure", parent, ["is_group", "parent_work_breakdown_structure"], (r) => {
//             if (r && r.is_group === 1) current_level++;
//             frm.set_value("wbs_level", current_level);
//             increment_level(frm, r.parent_work_breakdown_structure, current_level);
//         });
//     } else {
//         frm.set_value("wbs_level", current_level);
//     }
// }

function calculate_assigned_budget(frm) {
    let committed_budget = frm.doc.committed_overall_budget || 0;
    let actual_budget = frm.doc.actual_overall_budget || 0;
    let assigned_budget = committed_budget + actual_budget;
    frm.set_value("assigned_overall_budget", assigned_budget);
}

function calculate_available_budget(frm) {
    let overall_budget = frm.doc.overall_budget || 0;
    let assigned_overall_budget = frm.doc.assigned_overall_budget || 0;
    let available_budget = overall_budget - assigned_overall_budget;
    frm.set_value("available_budget", available_budget);
}


// function toggle_gl_account(frm) {
//     if (frm.doc.is_group === 1) {
//         frm.set_value('gl_account', null);
//         frm.refresh_field('gl_account');
//         frm.set_df_property('gl_account', 'reqd', 0);
//         frm.set_df_property('gl_account', 'hidden', 1);
//     } else {
//         frm.set_df_property('gl_account', 'hidden', 0);
//         frm.set_df_property('gl_account', 'reqd', 1);
//     }
// }

function toggle_gl_account(frm) {
    if (frm.doc.is_group) {
        frm.set_df_property('gl_account', 'reqd', 0);
        frm.set_df_property('gl_account', 'hidden', 1);
        if (frm.doc.gl_account) {
            frm.set_value('gl_account',null);
        }
    } else {
        frm.set_df_property('gl_account', 'reqd', 1);
        frm.set_df_property('gl_account', 'hidden', 0);
    }
}