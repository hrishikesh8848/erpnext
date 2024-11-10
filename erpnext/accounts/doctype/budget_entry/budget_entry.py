# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class BudgetEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		actual_overall_credit: DF.Currency
		actual_overall_debit: DF.Currency
		amended_from: DF.Link | None
		committed_overall_credit: DF.Currency
		committed_overall_debit: DF.Currency
		company: DF.Link | None
		document_date: DF.Date | None
		overall_credit: DF.Currency
		overall_debit: DF.Currency
		posting_date: DF.Data | None
		project: DF.Link | None
		voucher_no: DF.DynamicLink | None
		voucher_submit_date: DF.Datetime | None
		voucher_type: DF.Link | None
		wbs: DF.Link | None
		wbs_level: DF.Int
		wbs_name: DF.Data | None
		zero_budget: DF.Link | None
	# end: auto-generated types
	pass
