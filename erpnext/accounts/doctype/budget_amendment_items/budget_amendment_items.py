# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class BudgetAmendmentItems(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		decrement_budget: DF.Currency
		increment_budget: DF.Currency
		level: DF.Int
		overall_budget: DF.Currency
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		reason: DF.SmallText | None
		total: DF.Currency
		wbs_element: DF.Link | None
		wbs_name: DF.Data | None
	# end: auto-generated types
	pass
