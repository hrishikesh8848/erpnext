# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class GLClosing(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.gl_closing_details.gl_closing_details import GLClosingDetails
		from frappe.types import DF

		company: DF.Link
		end_date: DF.Date
		gl_closing_details: DF.Table[GLClosingDetails]
		period_name: DF.Data
		start_date: DF.Date
	# end: auto-generated types
	pass



import frappe
from frappe.utils import getdate, nowdate
@frappe.whitelist(allow_guest=True)
def validate_account_link_or_child_table(doc, method):
    if doc.doctype == "GL Entry" or doc.doctype == "GL Closing":
        return
    merged_data = get_merge()
    user_roles = get_user_roles()
    frozen_account_roles = get_account_settings()
    posting_date = doc.get("posting_date")
    if not posting_date:
        posting_date = nowdate()
    posting_date = getdate(posting_date)
    skip_validation = False
    for role_data in frozen_account_roles:
        frozen_accounts_modifier = role_data.get('frozen_accounts_modifier')
        if frozen_accounts_modifier and frozen_accounts_modifier in user_roles:
            skip_validation = True
            break
    if skip_validation:
        return  
    for record in merged_data:
        start_date = record.get("start_date")
        end_date = record.get("end_date")
        if start_date and end_date:
            start_date = getdate(start_date)
            end_date = getdate(end_date)
            if start_date <= posting_date <= end_date:
                for field in doc.meta.get("fields"):
                    if field.fieldtype == "Link" and field.options == "Account":
                        account_value = doc.get(field.fieldname)
                        if account_value:
                            if is_account_closed(merged_data, account_value):
                                frappe.throw(f"The account {account_value} is closed and cannot be used in this {doc.doctype}")
                        else:
                            frappe.throw(f"{field.label} is required")
                    elif field.fieldtype == "Table":
                        table_data = doc.get(field.fieldname)
                        if table_data:
                            for child_doc in table_data:
                                validate_child_table(child_doc, merged_data)
        else:
            frappe.msgprint(f"GL Closing record for {record.get('account')} has missing start or end date. Skipping account validation.")
def validate_child_table(child_doc, merged_data):
    for field in child_doc.meta.get("fields"):
        if field.fieldtype == "Link" and field.options == "Account":
            account_value = child_doc.get(field.fieldname)
            if account_value:
                if is_account_closed(merged_data, account_value):
                    frappe.throw(f"The account {account_value} is closed and cannot be used in this {child_doc.doctype}")
            else:
                frappe.throw(f"{field.label} in child table is required")
def is_account_closed(merged_data, account_value):
    for record in merged_data:
        if record.get("account") == account_value and record.get("closed") == 1:
            return True
    return False

@frappe.whitelist(allow_guest=True)
def get_merge():
    gl = frappe.qb.DocType("GL Closing")
    gl_details = frappe.qb.DocType("GL Closing Details")
    data = (
        frappe.qb.from_(gl)
        .left_join(gl_details).on(gl.name == gl_details.parent)
        .select(
            gl.name,
            gl.start_date,
            gl.end_date,
            gl_details.account,
            gl_details.closed
        )
        .run(as_dict=True)
    )
    return data
@frappe.whitelist(allow_guest=True)
def get_account_settings():
    acs = frappe.get_all("Accounts Closing Table", fields=["company", "frozen_accounts_modifier"])
    return acs
@frappe.whitelist(allow_guest=True)
def get_user_roles():
    user = frappe.session.user
    user_roles = frappe.get_roles(user)
    return user_roles



