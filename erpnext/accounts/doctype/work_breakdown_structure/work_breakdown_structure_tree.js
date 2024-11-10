frappe.provide("frappe.treeview_settings");

frappe.treeview_settings["Work Breakdown Structure"] = {
    breadcrumb: "Work Breakdown Structure",
    title: __("Work Breakdown Structure Tree"),
    get_tree_root: false,
    filters: [
        {
            fieldname: "project",
            fieldtype: "Link",
            options: "Project",
            label: __("Project"),
            on_change: function() {
                var me = frappe.treeview_settings["Work Breakdown Structure"].treeview;
                var project = me.page.fields_dict.project.get_value();
                if (!project) {
                    frappe.throw(__("Please set a Project"));
                }
            }
        },
    ],
    root_label: "Work Breakdown Structure",
    get_tree_nodes: 'erpnext.accounts.doctype.work_breakdown_structure.work_breakdown_structure.get_children',
    
    on_get_node: function(nodes, deep = false) {
        // Uncomment if needed
        // if (frappe.boot.user.can_read.indexOf("GL Entry") === -1) return;
    },
    add_tree_node: "erpnext.accounts.doctype.work_breakdown_structure.work_breakdown_structure.add_wbs_from_tree_view",
    fields: [
        {
            fieldtype: 'Link',
            fieldname: 'project',
            label: __('Project'),
            reqd: true,
            options: "Project"
        },
        {
            fieldtype: 'Data',
            fieldname: 'wbs_name',
            label: __('WBS Name'),
            reqd: true,
        },
        {
            fieldtype: 'Link',
            fieldname: 'company',
            label: __('Company'),
            reqd: true,
            options: "Company",
            default: frappe.defaults.get_user_default("Company")
        },
        {
            fieldtype: 'Check',
            fieldname: 'warehouse_required',
            label: __('Warehouse Required')
        },
        {
            fieldtype: 'Check',
            fieldname: 'is_group',
            label: __('Is Group'),
            description: __('Further nodes can only be created under Group type nodes')
        },
        {
            fieldtype: 'Button',
            fieldname: 'edit_full_form',
            label: __('Edit Full Form'),
            click: function() {
                console.log()
                console.log('1')
                var projectInput = document.querySelector('input[data-fieldname="project"]');
                console.log(projectInput)
                frappe.new_doc('Work Breakdown Structure', {
                    
                });
            }
        },
    ],
    toolbar: [
        {
            label: __("Edit"),
            click: function(node) {
                var wbs_label = node.label;
                var label_split = wbs_label.split(" : ");
                var wbs_id = label_split[0];
                frappe.set_route("Form", "Work Breakdown Structure", wbs_id);
            },
            btnClass: "hidden-xs"
        },
        {
            label: __("Delete"),
            click: function(node) {
                var wbs_label = node.label;
                var label_split = wbs_label.split(" : ");
                var wbs_id = label_split[0];
                frappe.confirm(__("Permanently delete {0}?", [wbs_id]), function() {
                    return frappe.call({
                        method: "erpnext.accounts.doctype.work_breakdown_structure.work_breakdown_structure.delete_wbs_from_tree_view",
                        args: {
                            "wbs": wbs_id
                        },
                        callback: function() {
                            frappe.call({
                                method: "frappe.client.delete",
                                args: {
                                    doctype: "Work Breakdown Structure",
                                    name: wbs_id
                                },
                                callback: function(r2) {
                                    if (!r2.exc) {
                                        frappe.utils.play_sound("delete");
                                        frappe.model.clear_doc("Work Breakdown Structure", wbs_id);
                                        frappe.msgprint(__("Deleted WBS - {0}", [wbs_id]));
                                    }
                                }
                            });
                        }
                    });
                });
            },
            btnClass: "hidden-xs"
        },
    ],
    extend_toolbar: true
};
