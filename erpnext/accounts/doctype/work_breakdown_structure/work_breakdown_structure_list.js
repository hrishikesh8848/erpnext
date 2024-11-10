frappe.listview_settings['Work Breakdown Structure'] = {
    //	add_fields: ["base_grand_total", "customer_name", "currency", "delivery_date",
    //		"per_delivered", "per_billed", "status", "order_type", "name", "skip_delivery_note"],
        hide_name_column: true,
        get_indicator: function (doc) {
            if (doc.locked) {
                // Pending Planning
                return [__("Locked &#128274;"), "red","status,=,Draft"];
            }
            else if (!doc.locked) {
                // Partially Planned
                return [__("Unlocked &#128275;"), "green","status,=,Draft"];
            }
            
            
            
                
        },
    };