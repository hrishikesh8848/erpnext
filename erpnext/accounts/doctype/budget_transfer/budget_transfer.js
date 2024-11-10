frappe.ui.form.on("Budget Transfer", {
    onload: function(frm) {
        // Set query for 'project' field without any specific filter
        frm.set_query("project", function() {
            return {}; // No filters applied
        });

        // Automatically set the document_date and posting_date to today's date
        // if (!frm.doc.document_date) {
        //     frm.set_value("document_date", frappe.datetime.get_today());
        // }
        if (!frm.doc.posting_date) {
            frm.set_value("posting_date", frappe.datetime.get_today());
        }

        frm.savecancel = function(btn, callback, on_error){ console.log("jiiri");return frm._cancel(btn, callback, on_error, false);}

    },
    
    from_wbs: function(frm) {
        // Check if 'from_wbs' field has a value
        if (frm.doc.from_wbs) {
            // Fetch 'wbs_name' and 'wbs_level' from the selected Work Breakdown Structure
            frappe.db.get_value("Work Breakdown Structure", frm.doc.from_wbs, ["wbs_name", "wbs_level","original_budget","overall_budget"], (r) => {
                if (r) {
                    frm.set_value("from_wbs_name", r.wbs_name);
                    frm.set_value("from_wbs_level", r.wbs_level);
					frm.set_value("fr_og_bgt", r.original_budget);
                    frm.set_value("fr_oa_bgt", r.overall_budget);
                }
            });
        } else {
            // Clear the fields if 'from_wbs' is not set
            frm.set_value("from_wbs_name", null);
            frm.set_value("from_wbs_level", null);
			frm.set_value("fr_og_bgt", null);
            frm.set_value("fr_oa_bgt", null);
        }
    },
	to_wbs: function(frm) {
        // Check if 'from_wbs' field has a value
        if (frm.doc.to_wbs) {
            // Fetch 'wbs_name' and 'wbs_level' from the selected Work Breakdown Structure
            frappe.db.get_value("Work Breakdown Structure", frm.doc.to_wbs, ["wbs_name", "wbs_level","original_budget","overall_budget"], (r) => {
                if (r) {
                    frm.set_value("to_wbs_name", r.wbs_name);
                    frm.set_value("to_wbs_level", r.wbs_level);
					frm.set_value("to_og_bgt", r.original_budget);
                    frm.set_value("to_oa_bgt", r.overall_budget);
                }
            });
        } else {
            // Clear the fields if 'from_wbs' is not set
            frm.set_value("to_wbs_name", null);
            frm.set_value("to_wbs_level", null);
			frm.set_value("to_og_bgt", null);
            frm.set_value("to_oa_bgt", null);
        }
    },

    from_project: function(frm) {
        // Check if 'from_project' field has a value
        if (frm.doc.from_project) {
            // Fetch 'project_name' and 'company' from the selected Project
            frappe.db.get_value("Project", frm.doc.from_project, ["project_name", "company"], (r) => {
                if (r) {
                    frm.set_value("from_project_name", r.project_name);
                    frm.set_value("company", r.company);
                }
            });
        } else {
            // Clear the fields if 'from_project' is not set
            frm.set_value("from_project_name", null);
            frm.set_value("company", null);
        }
    }
});
