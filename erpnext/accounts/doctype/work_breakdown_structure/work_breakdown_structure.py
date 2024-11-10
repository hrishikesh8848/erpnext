# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import (cint)
from frappe.query_builder.functions import Coalesce, Sum


class WorkBreakdownStructure(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.
     
	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		actual_overall_budget: DF.Currency
		amended_from: DF.Link | None
		assigned_overall_budget: DF.Currency
		available_budget: DF.Currency
		committed_overall_budget: DF.Currency
		company: DF.Link
		end_date: DF.Date | None
		gl_account: DF.Link | None
		is_group: DF.Check
		locked: DF.Check
		original_budget: DF.Currency
		overall_budget: DF.Currency
		parent_work_breakdown_structure: DF.Link | None
		project: DF.Link
		project_name: DF.Data | None
		project_type: DF.Data | None
		start_date: DF.Date | None
		wbs_level: DF.Data | None
		wbs_name: DF.Data
	# end: auto-generated types
   
from frappe import qb
from erpnext.accounts.report.financial_statements import sort_accounts

from frappe import qb
from erpnext.accounts.report.financial_statements import sort_accounts


@frappe.whitelist()
def get_children(doctype, parent, project, is_root=False):
    parent_fieldname = "parent_" + doctype.lower().replace(" ", "_")
    fields = [
        "CONCAT_WS(' : ', name, wbs_name) as value", 
        "is_group as expandable"
    ]
    filters = " where docstatus < 2 "
    
    if is_root:
        filters += """ and project = '{0}' """.format(project)
        filters += """ and coalesce({0}, '') = '' """.format(parent_fieldname)  # Use coalesce properly
    else:
        parts = parent.split(" : ")
        fields += [parent_fieldname + " as parent"]
        filters += """ and coalesce({0}, '') = '{1}' """.format(parent_fieldname, parts[0])  # Adjusting filter for non-root

    acc = frappe.db.sql("""
        SELECT CONCAT_WS(' : ', name, wbs_name) as value,
            is_group as expandable,
            {0} as parent
        FROM `tab{1}`
        {2} """.format(parent_fieldname, doctype, filters), as_dict=1)
    
    if doctype == "Account":
        sort_accounts(acc, is_root, key="value")

    return acc

@frappe.whitelist()
def add_wbs_from_tree_view(arguments=None):
    from frappe.desk.treeview import make_tree_args
    
    if not arguments:
        arguments = frappe.local.form_dict

    arguments.doctype = "Work Breakdown Structure"
    arguments = make_tree_args(**arguments)

    if arguments.get("parent"):
        parent = arguments.get("parent")
        parts = parent.split(" : ")
        arguments.update({
            "parent": parts[0]
        })

    if arguments.get("parent_work_breakdown_structure"):
        parent = arguments.get("parent_work_breakdown_structure")
        parts = parent.split(" : ")
        arguments.update({
            "parent_work_breakdown_structure": parts[0]
        })

    wbs = frappe.new_doc("Work Breakdown Structure")

    if arguments.get("ignore_permissions"):
        wbs.flags.ignore_permissions = True
        arguments.pop("ignore_permissions")

    wbs.update(arguments)

    if not wbs.parent_work_breakdown_structure:
        wbs.parent_work_breakdown_structure = arguments.get("parent")

    wbs.old_parent = ""
    if cint(wbs.get("is_root")):
        wbs.parent_work_breakdown_structure = None
        wbs.flags.ignore_mandatory = True

    wbs.insert()

    if int(arguments.get("warehouse_required")) == 1:
        create_warehouse(wbs.name)

    return wbs.name


@frappe.whitelist()
def delete_wbs_from_tree_view(wbs):
    if wbs:
        frappe.delete_doc('Work Breakdown Structure',wbs)
        # delete_warehouse(wbs)


# def validate_level(self):
#         if self.project_type:
#             max_level = frappe.db.get_value("Project Type",{'name':self.project_type},["custom_max_wbs_levels"])
#             if max_level > 0:
#                 if int(self.level) > int(max_level):
#                     msg = _("This Project Type has exceeded Maximum Allowed WBS Levels")
#                     frappe.throw(msg)


def after_insert(self):
    if self.is_wbs == 1:
        data = frappe.new_doc("Work Breakdown Structure")
        data.name = self.name
        print(self.name)
        data.project_type = self.project_type
        data.project_name = self.project_name
        data.company = self.company
        data.insert()
	

@frappe.whitelist()
def check_available_budget(wbs,amt,doctype):
        wbs_off = check_parent_wbs_budget(wbs, amt)
        wbs_doc = frappe.get_doc("Work Breakdown Structure", wbs_off[1])
        be = frappe.qb.DocType('Budget Entry')

        query = (
            frappe.qb.from_(be)
            .select(Sum(be.overall_credit - be.overall_debit).as_('sob'))
            .where(
                (be.wbs == wbs_doc.name) &
                (be.voucher_type.isin(["Supplementary Budget", "Budget Decrease", "Budget Transfer"])) &
                (be.original_entry == 0)
            )
        )
        statistical_amt = query.run(as_dict=True)
        
        ab = wbs_doc.available_budget - statistical_amt[0].get("sob") if statistical_amt[0].get("sob") else wbs_doc.available_budget
        cob = wbs_doc.committed_overall_budget
        aob = wbs_doc.actual_overall_budget
        ab_upd = ab
        wbs_id = ""
        if wbs:
            wbs_id = wbs_doc.name
            if doctype in ["Material Request" ,"Stock Entry","Budget Transfer","Budget Decrease", "Expense Claim", "Journal Entry"]:

                ab_upd = ab - amt
            if doctype in ["Purchase Order","Purchase Receipt"]:
                ab_upd = (ab + cob) - amt
            if doctype in ["Purchase Invoice"]:
                ab_upd = (ab + aob) - amt

        return [ab_upd, wbs_id]
