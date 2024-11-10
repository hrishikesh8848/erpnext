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
		total_amount: DF.Float
		wbs: DF.Link | None
		wbs_budget_items: DF.Table[WBSBudgetItems]
	# end: auto-generated types

	def validate(self):
		if self.total_amount and self.available_budget:
			if self.total_amount > self.available_budget:
				frappe.throw(_("Total amount cannot exceed the Available Budget."))

	def on_submit(self):
		total_budget_amount = 0
		for item in self.accounts:
			total_budget_amount += item.budget_amount
			create_child_wbs_budget(self, item)
			create_parent_wbs_budget(self, item)
			credit_to_child_wbs(self,item)

		debit_from_parent_wbs(self,total_budget_amount)

	def on_cancel(self):
		self.flags.ignore_links = True
		print("on cancel")

	def before_cancel(self):
		total_budget_amount = 0
		for item in self.accounts:
			total_budget_amount += item.budget_amount
			create_cancelled_child_budget_entries(self,item)
			create_cancelled_parent_budget_entries(self,item)
			debit_from_child_wbs(self,item)	

		credit_to_parent_wbs(self,total_budget_amount)


def credit_to_child_wbs(self,item):
	wbs = frappe.get_doc("Work Breakdown Structure",item.child_wbs)
	if item.budget_amount:
		wbs.overall_budget = wbs.overall_budget + item.budget_amount
	wbs.save(ignore_permissions=True)
	wbs.submit()  

def debit_from_child_wbs(self,item):
	wbs = frappe.get_doc("Work Breakdown Structure",item.child_wbs)
	if item.budget_amount:
		wbs.overall_budget = wbs.overall_budget - item.budget_amount
	wbs.save(ignore_permissions=True)
	wbs.submit()  

def create_cancelled_child_budget_entries(self,item):
	budget_entry = frappe.new_doc("Budget Entry")
	budget_entry.name = self.name
	budget_entry.project = self.project
	budget_entry.company = self.company

	if item.child_wbs:
		budget_entry.wbs = item.child_wbs

	if item.budget_amount:
		budget_entry.overall_debit = item.budget_amount

	wbs = frappe.get_doc("Work Breakdown Structure",item.child_wbs)
	if wbs.wbs_name:
		budget_entry.wbs_name = wbs.wbs_name

	if wbs.wbs_level:
		budget_entry.wbs_level = wbs.wbs_level
	
	budget_entry.voucher_no = self.name
	budget_entry.voucher_type = "WBS Budget"
	budget_entry.voucher_submit_date = now()

	budget_entry.insert()
	budget_entry.submit()

# 	update_wbs_after_cancellation(self)

# def update_wbs_after_cancellation(self):
# 	for row in self.accounts:
# 		wbs = frappe.get_doc("Work Breakdown Structure",row.child_wbs)
# 		if row.budget_amount:
# 			wbs.overall_budget -= row.budget_amount
# 		wbs.save()

def create_cancelled_parent_budget_entries(self,item):
	budget_entry = frappe.new_doc("Budget Entry")
	budget_entry.name = self.name
	budget_entry.project = self.project
	budget_entry.company = self.company

	budget_entry.wbs = self.wbs

	if item.budget_amount:
		budget_entry.overall_credit = item.budget_amount

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


def debit_from_parent_wbs(self,total_budget_amount):
	parent_wbs_account = frappe.get_doc("Work Breakdown Structure",self.wbs)
	parent_wbs_account.overall_budget -= total_budget_amount
	parent_wbs_account.save(ignore_permissions=True)
	parent_wbs_account.submit()  

def credit_to_parent_wbs(self,total_budget_amount):
	parent_wbs_account = frappe.get_doc("Work Breakdown Structure",self.wbs)
	parent_wbs_account.overall_budget += total_budget_amount
	parent_wbs_account.save(ignore_permissions=True)
	parent_wbs_account.submit()  

@frappe.whitelist()
def get_gl_accounts(wbs):
	child_wbs_records = frappe.get_all("Work Breakdown Structure", 
		filters= {"parent_work_breakdown_structure":wbs,"is_group":0},
		fields=["name","gl_account"]
	)
	return child_wbs_records

def create_child_wbs_budget(self, item):
	budget_entry = frappe.new_doc("Budget Entry")
	budget_entry.name = self.name
	budget_entry.project = self.project
	budget_entry.company = self.company

	if item.child_wbs:
		budget_entry.wbs = item.child_wbs

	if item.budget_amount:
		budget_entry.overall_credit = item.budget_amount

	wbs = frappe.get_doc("Work Breakdown Structure",item.child_wbs)
	if wbs.wbs_name:
		budget_entry.wbs_name = wbs.wbs_name

	if wbs.wbs_level:
		budget_entry.wbs_level = wbs.wbs_level
	
	budget_entry.voucher_no = self.name
	budget_entry.voucher_type = "WBS Budget"
	budget_entry.voucher_submit_date = now()

	budget_entry.insert()
	budget_entry.submit()

def create_parent_wbs_budget(self, item):
	budget_entry = frappe.new_doc("Budget Entry")
	budget_entry.name = self.name
	budget_entry.project = self.project
	budget_entry.company = self.company

	if self.wbs:
		budget_entry.wbs = self.wbs

	if item.budget_amount:
		budget_entry.overall_debit = item.budget_amount

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