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
    # end: auto-generated types
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    def on_submit(self):
        update_original_budget(self,"Submit")
       
    def on_cancel(self):
        self.flags.ignore_links = True

    def before_cancel(self):
        update_original_budget(self,"Cancel")

def update_original_budget(self,event):
    wbs_dict = []
    wbs_list = []
    if self.budget_amendment_items:
        for row in self.budget_amendment_items:
            if row.get("wbs_element") not in wbs_list:
                wbs_list.append(row.get("wbs_element"))
    if wbs_list:
        for i in wbs_list:
            wbs_dict.append({
                "wbs_id": i,
                "voucher_name":"",
                "voucher_type":"",
                "amount":0.0,
                "increment_amount":0.0,
                "decrement_amount":0.0
            })

    for row in self.budget_amendment_items:
        if row.get("increment_budget"):
            amount = row.get("increment_budget")
        elif row.get("decrement_budget"):
            amount = row.get("decrement_budget")

        if row.get("wbs_element"):
            for j in wbs_dict:
                if row.get("wbs_element") == j.get("wbs_id"):
                    if row.get("increment_budget"):
                        j.update({
                            "increment_amount": j.get("increment_amount") + amount,
                            "wbs_name": frappe.db.get_value("Work Breakdown Structure",row.get("wbs_element"), "wbs_name"),
                            "wbs_level":row.get("level"),
                            "txn_date":self.posting_date,
                            "voucher_type":self.doctype,
                            "voucher_name":self.name,
                        })
                    elif row.get("decrement_budget"):
                        j.update({
                            "decrement_amount": j.get("decrement_amount") - amount,
                            "wbs_name": frappe.db.get_value("Work Breakdown Structure",row.get("wbs_element"), "wbs_name"),
                            "wbs_level":row.get("level"),
                            "txn_date":self.posting_date,
                            "voucher_type":self.doctype,
                            "voucher_name":self.name,
                        })

            wbs_curr_doc = frappe.get_doc("Work Breakdown Structure",row.get("wbs_element"))
            if event == "Submit":                
                if row.get("increment_budget"):
                    wbs_curr_doc.overall_budget = wbs_curr_doc.overall_budget + amount
                else:
                    wbs_curr_doc.overall_budget = wbs_curr_doc.overall_budget - amount

                # wbs_curr_doc.assigned_overall_budget = wbs_curr_doc.actual_overall_budget + wbs_curr_doc.committed_overall_budget
                wbs_curr_doc.available_budget = wbs_curr_doc.overall_budget - wbs_curr_doc.assigned_overall_budget
                if wbs_curr_doc.locked:
                    frappe.throw(
                        "Transaction Not Allowed for  WBS Element - {0} as this WBS is locked !".format(wbs_curr_doc.name)
                    )
            elif event == "Cancel":
                if row.get("increment_budget"):
                    wbs_curr_doc.overall_budget = wbs_curr_doc.overall_budget - amount
                else:
                    wbs_curr_doc.overall_budget = wbs_curr_doc.overall_budget + amount

                # wbs_curr_doc.assigned_overall_budget = wbs_curr_doc.actual_overall_budget + wbs_curr_doc.committed_overall_budget
                wbs_curr_doc.available_budget = wbs_curr_doc.overall_budget - wbs_curr_doc.assigned_overall_budget
                if wbs_curr_doc.locked:
                    frappe.throw(
                        "Transaction Not Allowed for  WBS Element - {0} as this WBS is locked !".format(wbs_curr_doc.name)
                    )
            wbs_curr_doc.save(ignore_permissions=True)

    if wbs_dict:
        for i in wbs_dict:
            create_budget_entry(self,i,event,self.company) 
    
def create_budget_entry(self,row,event,company):
    if row.get("wbs_id"):
        bgt_ent = frappe.new_doc("Budget Entry")
        bgt_ent.project = self.project
        bgt_ent.wbs = row.get("wbs_id")
        bgt_ent.wbs_name = row.get("wbs_name")
        bgt_ent.wbs_level = row.get("wbs_level")
        bgt_ent.company = company
        bgt_ent.posting_date = self.posting_date
        if event == "Submit":
            if row.get("increment_amount"):
                bgt_ent.overall_credit = row.get("increment_amount")
            elif row.get("decrement_amount"):
                bgt_ent.overall_debit = abs(row.get("decrement_amount"))       
        elif event == "Cancel":
            if row.get("increment_amount"):
                bgt_ent.overall_debit = row.get("increment_amount")
            elif row.get("decrement_amount"):
                bgt_ent.overall_credit = abs(row.get("decrement_amount"))

        bgt_ent.voucher_type = "Budget Amendment"
        bgt_ent.voucher_no = self.name
        bgt_ent.voucher_submit_date = now()
        bgt_ent.save(ignore_permissions=True)
        bgt_ent.submit()
