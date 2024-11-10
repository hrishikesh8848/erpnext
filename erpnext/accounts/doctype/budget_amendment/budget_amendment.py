# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now

class BudgetAmendment(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from erpnext.accounts.doctype.budget_amendment_items.budget_amendment_items import BudgetAmendmentItems
        from frappe.types import DF

        amended_from: DF.Link | None
        budget_amendment_items: DF.Table[BudgetAmendmentItems]
        company: DF.Data | None
        posting_date: DF.Data | None
        project: DF.Link | None
        project_name: DF.Data | None
        total_decrement_budget: DF.Data | None
        total_increment_budget: DF.Data | None
        total_overall_budget: DF.Data | None

    def on_submit(self):
        for item in self.budget_amendment_items:
            budget_entry = frappe.new_doc("Budget Entry")
            budget_entry.name = self.name
            budget_entry.project = self.project
            budget_entry.company = self.company
            budget_entry.posting_date = self.posting_date
            # budget_entry.document_date = self.document_date

            if item.wbs_name:
                budget_entry.wbs_name = item.wbs_name

            if item.wbs_element:
                budget_entry.wbs = item.wbs_element

            if item.level:
                budget_entry.wbs_level = item.level

            if item.increment_budget:
                budget_entry.overall_credit = item.increment_budget
            
            if item.decrement_budget:
                budget_entry.overall_debit = item.decrement_budget
            
            budget_entry.voucher_no = self.name
            budget_entry.voucher_type = "Budget Amendment"
            budget_entry.voucher_submit_date = now()

            budget_entry.insert()
            budget_entry.submit()

        update_wbs(self)

    def on_cancel(self):
        self.flags.ignore_links = True
        print("on cancel")

    def before_cancel(self):
        create_cancelled_budget_entries(self)

def update_wbs(self):
    for row in self.budget_amendment_items:
        wbs = frappe.get_doc("Work Breakdown Structure",row.wbs_element)
        if row.increment_budget:
            wbs.overall_budget += row.increment_budget
        elif row.decrement_budget:
            wbs.overall_budget -= row.decrement_budget
        wbs.save()

def create_cancelled_budget_entries(self):
    for item in self.budget_amendment_items:
        budget_entry = frappe.new_doc("Budget Entry")
        budget_entry.name = self.name
        budget_entry.project = self.project
        budget_entry.company = self.company
        budget_entry.posting_date = self.posting_date
        # budget_entry.document_date = self.document_date

        if item.wbs_name:
            budget_entry.wbs_name = item.wbs_name

        if item.wbs_element:
            budget_entry.wbs = item.wbs_element

        if item.level:
            budget_entry.wbs_level = item.level

        if item.increment_budget:
            budget_entry.overall_debit = item.increment_budget
        
        if item.decrement_budget:
            budget_entry.overall_credit = item.decrement_budget
        
        budget_entry.voucher_no = self.name
        budget_entry.voucher_type = "Budget Amendment"
        budget_entry.voucher_submit_date = now()

        budget_entry.insert()
        budget_entry.submit()

    update_wbs_after_cancellation(self)

def update_wbs_after_cancellation(self):
    for row in self.budget_amendment_items:
        wbs = frappe.get_doc("Work Breakdown Structure",row.wbs_element)
        if row.increment_budget:
            wbs.overall_budget -= row.increment_budget
        elif row.decrement_budget:
            wbs.overall_budget += row.decrement_budget
        wbs.save()

    # # end: auto-generated types
    # def before_submit(self):
    #     budget_amendment_items = frappe.get_all(
    #         "Budget Amendment Items", 
    #         filters={"parent": self.name}, 
    #         fields=["wbs_element", "increment_budget", "decrement_budget"]
    #     )
        
    #     for item in budget_amendment_items:
    #         if item.get("wbs_element"):
    #             wbs = frappe.get_doc("Work Breakdown Structure", item["wbs_element"])
    #             if item.get("increment_budget"):
    #                 wbs.overall_budget += item["increment_budget"]
    #             if item.get("decrement_budget"):
    #                 wbs.overall_budget -= item["decrement_budget"]
    #             wbs.save()
    #     return

    # def on_submit(self):
    #     # Loop through budget_amendment_items to create new Budget Entry records
    #     for item in self.budget_amendment_items:
    #         data = frappe.new_doc("Budget Entry")
    #         data.budget_amendment = self.name  # Link Budget Entry to the Budget Amendment record
    #         data.project = self.project
    #         data.company = self.company
    #         data.posting_date = self.posting_date
    #         # data.document_date = self.document_date

    #         # Assign values based on conditions
    #         data.wbs_name = item.wbs_name if item.get("wbs_name") else None
    #         data.wbs = item.wbs_element if item.get("wbs_element") else None
    #         data.wbs_level = item.level if item.get("level") else None
    #         data.overall_credit = item.increment_budget if item.get("increment_budget") else 0
    #         data.overall_debit = item.decrement_budget if item.get("decrement_budget") else 0

    #         # Insert the new document into the database
    #         data.insert()