# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now
from frappe import _

class WBSBudget(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.budget_account.budget_account import BudgetAccount
		from erpnext.accounts.doctype.wbs_budget_items.wbs_budget_items import WBSBudgetItems
		from frappe.types import DF

		accounts: DF.Table[BudgetAccount]
		action_if_accumulated_monthly_budget_exceeded: DF.Literal["", "Stop", "Warn", "Ignore"]
		action_if_accumulated_monthly_budget_exceeded_on_mr: DF.Literal["", "Stop", "Warn", "Ignore"]
		action_if_accumulated_monthly_budget_exceeded_on_po: DF.Literal["", "Stop", "Warn", "Ignore"]
		action_if_annual_budget_exceeded: DF.Literal["", "Stop", "Warn", "Ignore"]
		action_if_annual_budget_exceeded_on_mr: DF.Literal["", "Stop", "Warn", "Ignore"]
		action_if_annual_budget_exceeded_on_po: DF.Literal["", "Stop", "Warn", "Ignore"]
		amended_from: DF.Link | None
		applicable_on_booking_actual_expenses: DF.Check
		applicable_on_material_request: DF.Check
		applicable_on_purchase_order: DF.Check
		available_budget: DF.Currency
		budget_against: DF.Literal["", "Cost Center", "Project"]
		company: DF.Link | None
		cost_center: DF.Link | None
		fiscal_year: DF.Link | None
		from_date: DF.Date | None
		monthly_distribution: DF.Link | None
		project: DF.Link | None
		to_date: DF.Date | None
		total: DF.Int
		total_amount: DF.Float
		wbs: DF.Link | None
		wbs_budget_items: DF.Table[WBSBudgetItems]
	# end: auto-generated types

	def validate(self):
		if self.total_amount and self.available_budget:
			if self.total_amount > self.available_budget:
				frappe.throw(_("Total amount cannot exceed the Available Budget."))

	def on_cancel(self):
		self.flags.ignore_links = True
			
	def on_submit(self):
		update_original_budget(self,"Submit")
			
	def before_cancel(self):
		update_original_budget(self,"Cancel")

@frappe.whitelist()
def get_gl_accounts(wbs):
	child_wbs_records = frappe.get_all("Work Breakdown Structure", 
		filters= {"parent_work_breakdown_structure":wbs,"is_group":0},
		fields=["name","gl_account"]
	)
	return child_wbs_records

def update_original_budget(self,event):
	wbs_dict = []
	wbs_list = []
	if self.accounts:
		for row in self.accounts:
			if row.get("child_wbs") not in wbs_list:
				wbs_list.append(row.get("child_wbs"))
	if wbs_list:
		for i in wbs_list:
			wbs_dict.append({
				"wbs_id": i,
				"voucher_name":"",
				"voucher_type":"",
				"amount":0.0
			})

	for row in self.accounts:
		amount = row.get("budget_amount")
		if row.get("child_wbs"):
			for j in wbs_dict:
				if row.get("child_wbs") == j.get("wbs_id"):
					wbs_name,wbs_level = frappe.db.get_value("Work Breakdown Structure",row.get("child_wbs"),['wbs_name','wbs_level'])
					j.update({
						"amount": j.get("amount") + row.get("budget_amount"),
						"wbs_name": wbs_name,
						"wbs_level":wbs_level,
						"voucher_type":self.doctype,
						"voucher_name":self.name,
						"increment_budget": row.get("increment_budget"),
						"decrement_budget": row.get("decrement_budget")
					})
			wbs_curr_doc = frappe.get_doc("Work Breakdown Structure",row.get("child_wbs"))
			if event == "Submit":
				wbs_curr_doc.overall_budget = wbs_curr_doc.overall_budget + amount

				wbs_curr_doc.assigned_overall_budget = wbs_curr_doc.actual_overall_budget + wbs_curr_doc.committed_overall_budget
				wbs_curr_doc.available_budget = wbs_curr_doc.overall_budget - wbs_curr_doc.assigned_overall_budget
				if wbs_curr_doc.locked:
					frappe.throw(
						"Transaction Not Allowed for  WBS Element - {0} as this WBS is locked !".format(wbs_curr_doc.name)
					)
			elif event == "Cancel":
				wbs_curr_doc.overall_budget = wbs_curr_doc.overall_budget - amount

				wbs_curr_doc.assigned_overall_budget = wbs_curr_doc.actual_overall_budget + wbs_curr_doc.committed_overall_budget
				wbs_curr_doc.available_budget = wbs_curr_doc.overall_budget - wbs_curr_doc.assigned_overall_budget
				if wbs_curr_doc.locked:
					frappe.throw(
						"Transaction Not Allowed for  WBS Element - {0} as this WBS is locked !".format(wbs_curr_doc.name)
					)
			wbs_curr_doc.save(ignore_permissions=True)

	
	total_amt = 0
	for row in self.accounts:
		total_amt += row.budget_amount

	wbs_parent = frappe.get_doc("Work Breakdown Structure",self.wbs)
	if event == "Submit":
		wbs_parent.overall_budget = wbs_parent.overall_budget - total_amt
		wbs_parent.available_budget = wbs_parent.overall_budget - wbs_parent.assigned_overall_budget	
		if wbs_parent.locked:
			frappe.throw(
				"Transaction Not Allowed for  WBS Element - {0} as this WBS is locked !".format(wbs_parent.name)
			)
	elif event == "Cancel":
		wbs_parent.overall_budget = wbs_parent.overall_budget + total_amt
		wbs_parent.available_budget = wbs_parent.overall_budget - wbs_parent.assigned_overall_budget
		if wbs_parent.locked:
			frappe.throw(
				"Transaction Not Allowed for  WBS Element - {0} as this WBS is locked !".format(wbs_parent.name)
			)
	wbs_parent.save(ignore_permissions=True)

	if wbs_dict:
		for i in wbs_dict:
			create_budget_entry(self,i,event,self.company)
		create_parent_wbs_budget_entry(self,event) 
    
def create_budget_entry(self,row,event,company):
    if row.get("wbs_id"):
        bgt_ent = frappe.new_doc("Budget Entry")
        bgt_ent.project = self.project
        bgt_ent.wbs = row.get("wbs_id")
        bgt_ent.wbs_name = row.get("wbs_name")
        bgt_ent.wbs_level = row.get("wbs_level")
        bgt_ent.company = company
        if event == "Submit":
            bgt_ent.overall_credit = row.get("amount")            
        elif event == "Cancel":
            bgt_ent.overall_debit = row.get("amount")   

        bgt_ent.voucher_type = "WBS Budget"
        bgt_ent.voucher_no = self.name
        bgt_ent.voucher_submit_date = now()
        bgt_ent.save(ignore_permissions=True)
        bgt_ent.submit()
        

def create_parent_wbs_budget_entry(self,event):
	budget_entry = frappe.new_doc("Budget Entry")
	budget_entry.name = self.name
	budget_entry.project = self.project
	budget_entry.company = self.company

	if self.wbs:
		budget_entry.wbs = self.wbs

	if self.accounts:
		total_amt = 0
		for row in self.accounts:
			total_amt += row.budget_amount

	if event == "Submit":
		budget_entry.overall_debit = total_amt
	elif event == "Cancel":
		budget_entry.overall_credit = total_amt
	# if item.budget_amount:
	# 	budget_entry.overall_debit = item.budget_amount

	wbs = frappe.get_doc("Work Breakdown Structure",self.wbs)
	if wbs.wbs_name:
		budget_entry.wbs_name = wbs.wbs_name

	if wbs.wbs_level:
		budget_entry.wbs_level = wbs.wbs_level
	
	budget_entry.voucher_no = self.name
	budget_entry.voucher_type = "WBS Budget"
	budget_entry.voucher_submit_date = now()

	budget_entry.insert()
	budget_entry.submit()
