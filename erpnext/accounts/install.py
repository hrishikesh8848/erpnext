FIELD_MAPPING = {
    "Accounts Settings": [
        {
            "fieldname": "section_break",
            "label": "Section Break",
            "fieldtype": "Section Break",
            "insert_after": "frozen_accounts_modifier",
            
        },
        {
            "fieldname": "accounts_closing_table",
            "label": "Accounts Closing Table",
            "fieldtype": "Table",
            "insert_after": "section_break",  
            "options": "Accounts Closing Table",
        }
    ]
}

def create_custom_fields():
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
    create_custom_fields(FIELD_MAPPING)

def after_migrate():
    create_custom_fields()
