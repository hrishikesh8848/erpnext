# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from datetime import datetime
import frappe
from frappe.model.document import Document
from frappe.utils.data import getdate
from frappe.utils import now
from erpnext.accounts.doctype.work_breakdown_structure.work_breakdown_structure import check_available_budget

class BudgetTransfer(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		budget_amount: DF.Currency
		company: DF.Link | None
		fr_oa_bgt: DF.Currency
		fr_og_bgt: DF.Currency
		from_project: DF.Link | None
		from_project_name: DF.Data | None
		from_wbs: DF.Link | None
		from_wbs_level: DF.Data | None
		from_wbs_name: DF.Data | None
		posting_date: DF.Date | None
		reason: DF.Text | None
		to_oa_bgt: DF.Currency
		to_og_bgt: DF.Currency
		to_wbs: DF.Link | None
		to_wbs_level: DF.Data | None
		to_wbs_name: DF.Data | None
	# end: auto-generated types
	# Copyright (c) 2023, 8848 Digital LLP and contributors
	# For license information, please see license.txt

	def on_submit(self):
		create_debit_wbs_budget_entry(self)
		create_credit_wbs_budget_entry(self)

	def on_cancel(self):
		self.flags.ignore_links = True
	
	def before_cancel(self):
		create_cancelled_debit_wbs_budget_entry(self)
		create_cancelled_credit_wbs_budget_entry(self)

def create_debit_wbs_budget_entry(self):
	budget_entry = frappe.new_doc("Budget Entry")
	budget_entry.project = self.from_project
	budget_entry.company = self.company
	budget_entry.wbs = self.from_wbs
	budget_entry.wbs_name = self.from_wbs_name
	budget_entry.wbs_level = self.from_wbs_level
	budget_entry.overall_debit = self.budget_amount
	budget_entry.voucher_no = self.name
	budget_entry.voucher_type = "Budget Transfer"
	budget_entry.posting_date = frappe.utils.nowdate()
	budget_entry.save()
	budget_entry.submit()
	update_debit_wbs(budget_entry)


def create_credit_wbs_budget_entry(self):
	budget_entry = frappe.new_doc("Budget Entry")
	budget_entry.project = self.from_project
	budget_entry.company = self.company
	budget_entry.wbs = self.to_wbs
	budget_entry.wbs_name = self.to_wbs_name
	budget_entry.wbs_level = self.to_wbs_level
	budget_entry.overall_credit = self.budget_amount
	budget_entry.voucher_no = self.name
	budget_entry.voucher_type = "Budget Transfer"
	budget_entry.posting_date = frappe.utils.nowdate()
	budget_entry.save()
	budget_entry.submit()
	update_credit_wbs(budget_entry)

def update_debit_wbs(budget_entry):
	wbs = frappe.get_doc("Work Breakdown Structure",budget_entry.wbs)
	wbs.overall_budget -= budget_entry.overall_debit
	wbs.save()

def update_credit_wbs(budget_entry):
	wbs = frappe.get_doc("Work Breakdown Structure",budget_entry.wbs)
	wbs.overall_budget += budget_entry.overall_credit
	wbs.save()

def create_cancelled_debit_wbs_budget_entry(self):
	budget_entry = frappe.new_doc("Budget Entry")
	budget_entry.project = self.from_project
	budget_entry.company = self.company
	budget_entry.wbs = self.from_wbs
	budget_entry.wbs_name = self.from_wbs_name
	budget_entry.wbs_level = self.from_wbs_level
	budget_entry.overall_credit = self.budget_amount
	budget_entry.voucher_no = self.name
	budget_entry.voucher_type = "Budget Transfer"
	budget_entry.posting_date = frappe.utils.nowdate()
	budget_entry.save()
	budget_entry.submit()
	update_debit_wbs_after_cancel(budget_entry)

def	create_cancelled_credit_wbs_budget_entry(self):
	budget_entry = frappe.new_doc("Budget Entry")
	budget_entry.project = self.from_project
	budget_entry.company = self.company
	budget_entry.wbs = self.to_wbs
	budget_entry.wbs_name = self.to_wbs_name
	budget_entry.wbs_level = self.to_wbs_level
	budget_entry.overall_debit = self.budget_amount
	budget_entry.voucher_no = self.name
	budget_entry.voucher_type = "Budget Transfer"
	budget_entry.posting_date = frappe.utils.nowdate()
	budget_entry.save()
	budget_entry.submit()
	update_credit_wbs_after_cancel(budget_entry)

def update_debit_wbs_after_cancel(budget_entry):
	wbs = frappe.get_doc("Work Breakdown Structure",budget_entry.wbs)
	wbs.overall_budget += budget_entry.overall_credit
	wbs.save()

def update_credit_wbs_after_cancel(budget_entry):
	wbs = frappe.get_doc("Work Breakdown Structure",budget_entry.wbs)
	wbs.overall_budget -= budget_entry.overall_debit
	wbs.save()