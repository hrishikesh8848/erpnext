# Copyright (c) 2024, VINOD GAJJALA and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate


class PaymentReconciliationRecord(Document):
	def on_submit(self):
		self.create_payment_ledger_entries()
		self.update_invoice_status()


	def update_invoice_status(self):
		if self.allocation:
			for d in self.allocation:
				ref_doc = frappe.get_doc(d.invoice_type, d.invoice_number)
				if d.unreconcile == 0:
					outstanding1=self.get_outstanding_amount(d.invoice_type, d.invoice_number, d.reference_type, d.reference_name,d.unreconcile,d.allocated_amount)
					frappe.log_error("outstanding2",outstanding1)
					ref_doc.outstanding_amount = (
					    outstanding1 or 0.0
					)
					frappe.db.set_value(
					    d.invoice_type, d.invoice_number,
					    "outstanding_amount",
					    outstanding1 or 0.0,
					)

					
					
				elif d.unreconcile == 1:
					outstanding2=self.get_outstanding_amount(d.invoice_type, d.invoice_number, d.reference_type, d.reference_name,d.unreconcile,d.allocated_amount)

				ref_doc.set_status(update=True)
				ref_doc.notify_update()


	def get_outstanding_amount(self,invoice_type, invoice_number, reference_type, reference_name,unreconcile,allocated_amount):
		# Get grand total of the invoice
		invoice_data = frappe.db.sql("""
			SELECT name, grand_total
			FROM `tab{invoice_type}`
			WHERE name = %s
		""".format(invoice_type=invoice_type), (invoice_number,), as_dict=True)

		if not invoice_data:
			frappe.throw("Invoice not found")

		grand_total = invoice_data[0].grand_total
		

		# Get total payments made against this invoice

		total_paid = allocated_amount

		if unreconcile == 0:
			outstanding = grand_total - total_paid
			return outstanding
		elif unreconcile == 1:
			invoice_datas = frappe.db.sql("""
					SELECT name, outstanding_amount
					FROM `tab{invoice_type}`
					WHERE name = %s
				""".format(invoice_type=invoice_type), (invoice_number,), as_dict=True)

			if not invoice_data:
				frappe.throw("Invoice not found")

			grand_totals = invoice_datas[0].outstanding_amount
			# frappe.throw(str(grand_totals))
			frappe.log_error("invoice_datas",invoice_datas)
			frappe.log_error("grand_totals",grand_totals)
			outstanding=total_paid
			return outstanding

		
	def on_cancel(self):
		frappe.throw(_("Cancelling records is not allowed."))

	def create_payment_ledger_entries(self):
		"""Create Payment Ledger Entries for each allocation"""
		for allocation in self.allocation:
			if allocation.unreconcile:
				continue
				
			account_type = "Receivable" if self.party_type == "Customer" else "Payable"
			
			self.create_payment_ledger_entry(
				accounting_entry="Credit" if account_type == "Receivable" else "Debit",
				party_type=self.party_type,
				party=self.party,
				amount=abs(flt(allocation.allocated_amount)),
				account=self.default_advance_account if frappe.db.get_value("Company",self.company,"book_advance_payments_in_separate_party_account") else self.receivable__payable_account,
				reference_type=allocation.reference_type,
				reference_name=allocation.reference_name,
				against_voucher_type=allocation.invoice_type,
				against_voucher_no=allocation.invoice_number,
				cost_center=allocation.cost_center,
				exchange_rate=allocation.exchange_rate,
				currency=allocation.currency
			)

	def create_payment_ledger_entry(self, **kwargs):
		"""Create a new Payment Ledger Entry"""
		ple = frappe.new_doc("Payment Ledger Entry")
		ple.posting_date = self.clearing_date or nowdate()
		ple.company = self.company
		ple.account_type = "Receivable" if self.party_type == "Customer" else "Payable"
		ple.account = kwargs.get("account")
		ple.party_type = kwargs.get("party_type")
		ple.party = kwargs.get("party")
		ple.cost_center = kwargs.get("cost_center")
			
		ple.voucher_type =kwargs.get('reference_type')
		ple.voucher_no = kwargs.get('reference_name')
		ple.against_voucher_type = kwargs.get("against_voucher_type")
		ple.against_voucher_no = kwargs.get("against_voucher_no")
		ple.amount = kwargs.get("amount") if kwargs.get("currency") == "INR" else float(kwargs.get("amount"))* float(kwargs.get("exchange_rate"))
		ple.account_currency= kwargs.get("currency")
		ple.amount_in_account_currency=kwargs.get("amount")
		
		ple.remarks = f"Against {kwargs.get('against_voucher_type')} {kwargs.get('against_voucher_no')}"
		
		ple.flags.ignore_permissions = True
		ple.submit()
		