# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import copy

import frappe
from frappe import _
from frappe.query_builder.functions import IfNull, Sum
from frappe.utils import date_diff, flt, getdate


def execute(filters=None):
	if not filters:
		return [], []

	validate_filters(filters)

	columns = get_columns(filters)
	data = get_data(filters)
	

	if not data:
		return [], [], None, []
	
	update_received_amount(data)

	data, chart_data = prepare_data(data, filters)

	return columns, data, None, chart_data


def validate_filters(filters):
	from_date, to_date = filters.get("from_date"), filters.get("to_date")

	if not from_date and to_date:
		frappe.throw(_("From and To Dates are required."))
	elif date_diff(to_date, from_date) < 0:
		frappe.throw(_("To Date cannot be before From Date."))


def get_data(filters):
    is_projects_installed = "projects" in frappe.get_installed_apps()
    query_result = frappe.db.sql(
        f"""SELECT 
                "tabPurchase Order"."transaction_date" AS "date",
                "tabPurchase Order Item"."schedule_date" AS "required_date",
                {'"tabPurchase Order Item"."project",' if is_projects_installed else ''}
                "tabPurchase Order"."name" AS "purchase_order",
                "tabPurchase Order"."status",
                "tabPurchase Order"."supplier",
                "tabPurchase Order Item"."item_code",
                "tabPurchase Order Item"."qty",
                "tabPurchase Order Item"."received_qty",
                "tabPurchase Order Item"."qty" - "tabPurchase Order Item"."received_qty" AS "pending_qty",
                SUM(COALESCE("tabPurchase Invoice Item"."qty", 0)) AS "billed_qty",
                "tabPurchase Order Item"."base_amount" AS "amount",
                "tabPurchase Order Item"."billed_amt" * COALESCE("tabPurchase Order"."conversion_rate", 1) AS "billed_amount",
                "tabPurchase Order Item"."base_amount" - ("tabPurchase Order Item"."billed_amt" * COALESCE("tabPurchase Order"."conversion_rate", 1)) AS "pending_amount",
                "tabPurchase Order"."set_warehouse" AS "warehouse",
                "tabPurchase Order"."company",
                "tabPurchase Order Item"."name",
                (ARRAY_AGG("tabPurchase Invoice Item"."name"))[1] AS "invoice_items"
            FROM 
                "tabPurchase Order"
            JOIN 
                "tabPurchase Order Item" 
                ON "tabPurchase Order Item"."parent" = "tabPurchase Order"."name"
            LEFT JOIN 
                "tabPurchase Invoice Item" 
                ON "tabPurchase Invoice Item"."po_detail" = "tabPurchase Order Item"."name" 
                AND "tabPurchase Invoice Item"."docstatus" = 1
            WHERE 
                "tabPurchase Order"."status" NOT IN ('Stopped', 'Closed')
                AND "tabPurchase Order"."docstatus" = 1
                
            GROUP BY 
                "tabPurchase Order"."transaction_date",
                "tabPurchase Order Item"."schedule_date",
                {'"tabPurchase Order Item"."project",' if is_projects_installed else ''}
                "tabPurchase Order"."name",
                "tabPurchase Order"."status",
                "tabPurchase Order"."supplier",
                "tabPurchase Order Item"."item_code",
                "tabPurchase Order Item"."qty",
                "tabPurchase Order Item"."received_qty",
                "tabPurchase Order Item"."base_amount",
                "tabPurchase Order Item"."billed_amt",
                "tabPurchase Order"."conversion_rate",
                "tabPurchase Order"."set_warehouse",
                "tabPurchase Order"."company",
                "tabPurchase Order Item"."name"
            ORDER BY 
                "tabPurchase Order"."transaction_date";
        """,
        as_dict=True
    )
    filtered_data = []
    
    for row in query_result:
        include_row = True
        
        if filters.get("company") and row["company"] != filters.get("company"):
            include_row = False
            
        if filters.get("name") and row["purchase_order"] != filters.get("name"):
            include_row = False
            
        if filters.get("from_date") and filters.get("to_date"):
            if not ((getdate(filters.get("from_date")) <= row["date"]) and (row["date"] <= getdate(filters.get("to_date")))):
                include_row = False
                
        if filters.get("status"):
            if isinstance(filters["status"], list):
                if row["status"] not in filters["status"]:
                    include_row = False
            else:
                if row["status"] != filters["status"]:
                    include_row = False
                    
        if filters.get("project") and row["project"] != filters.get("project"):
            include_row = False
            
        if include_row:
            filtered_data.append(row)

    return filtered_data

def update_received_amount(data):
	pr_data = get_received_amount_data(data)
	for row in data:
		row.received_qty_amount = flt(pr_data.get(row.name))
  
def get_received_amount_data(data):
	pr = frappe.qb.DocType("Purchase Receipt")
	pr_item = frappe.qb.DocType("Purchase Receipt Item")

	po_items = [row.name for row in data]
	if not po_items:
		return frappe._dict()
	

	query = (
		frappe.qb.from_(pr)
		.inner_join(pr_item)
		.on(pr_item.parent == pr.name)
		.select(
			pr_item.purchase_order_item,
			Sum(pr_item.base_amount).as_("received_qty_amount"),
		)
		.where((pr.docstatus == 1) & (pr_item.purchase_order_item.isin(po_items)))
		.groupby(pr_item.purchase_order_item)
	)

	data = query.run()
	if not data:
		return frappe._dict()
	return frappe._dict(data)


def prepare_data(data, filters):
	completed, pending = 0, 0
	pending_field = "pending_amount"
	completed_field = "billed_amount"

	if filters.get("group_by_po"):
		purchase_order_map = {}

	for row in data:
		# sum data for chart
		completed += row[completed_field]
		pending += row[pending_field]

		# prepare data for report view
		row["qty_to_bill"] = flt(row["qty"]) - flt(row["billed_qty"])

		if filters.get("group_by_po"):
			po_name = row["purchase_order"]

			if po_name not in purchase_order_map:
				# create an entry
				row_copy = copy.deepcopy(row)
				purchase_order_map[po_name] = row_copy
			else:
				# update existing entry
				po_row = purchase_order_map[po_name]
				po_row["required_date"] = min(getdate(po_row["required_date"]), getdate(row["required_date"]))

				# sum numeric columns
				fields = [
					"qty",
					"received_qty",
					"pending_qty",
					"billed_qty",
					"qty_to_bill",
					"amount",
					"received_qty_amount",
					"billed_amount",
					"pending_amount",
				]
				for field in fields:
					po_row[field] = flt(row[field]) + flt(po_row[field])

	chart_data = prepare_chart_data(pending, completed)

	if filters.get("group_by_po"):
		data = []
		for po in purchase_order_map:
			data.append(purchase_order_map[po])
		return data, chart_data

	return data, chart_data


def prepare_chart_data(pending, completed):
	labels = ["Amount to Bill", "Billed Amount"]

	return {
		"data": {"labels": labels, "datasets": [{"values": [pending, completed]}]},
		"type": "donut",
		"height": 300,
	}


def get_columns(filters):
	columns = [
		{"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 90},
		{"label": _("Required By"), "fieldname": "required_date", "fieldtype": "Date", "width": 90},
		{
			"label": _("Purchase Order"),
			"fieldname": "purchase_order",
			"fieldtype": "Link",
			"options": "Purchase Order",
			"width": 160,
		},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 130},
		{
			"label": _("Supplier"),
			"fieldname": "supplier",
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 130,
		},
		{
			"label": _("Project"),
			"fieldname": "project",
			"fieldtype": "Link",
			"options": "Project",
			"width": 130,
		},
	]

	if not filters.get("group_by_po"):
		columns.append(
			{
				"label": _("Item Code"),
				"fieldname": "item_code",
				"fieldtype": "Link",
				"options": "Item",
				"width": 100,
			}
		)

	columns.extend(
		[
			{
				"label": _("Qty"),
				"fieldname": "qty",
				"fieldtype": "Float",
				"width": 120,
				"convertible": "qty",
			},
			{
				"label": _("Received Qty"),
				"fieldname": "received_qty",
				"fieldtype": "Float",
				"width": 120,
				"convertible": "qty",
			},
			{
				"label": _("Pending Qty"),
				"fieldname": "pending_qty",
				"fieldtype": "Float",
				"width": 80,
				"convertible": "qty",
			},
			{
				"label": _("Billed Qty"),
				"fieldname": "billed_qty",
				"fieldtype": "Float",
				"width": 80,
				"convertible": "qty",
			},
			{
				"label": _("Qty to Bill"),
				"fieldname": "qty_to_bill",
				"fieldtype": "Float",
				"width": 80,
				"convertible": "qty",
			},
			{
				"label": _("Amount"),
				"fieldname": "amount",
				"fieldtype": "Currency",
				"width": 110,
				"options": "Company:company:default_currency",
				"convertible": "rate",
			},
			{
				"label": _("Billed Amount"),
				"fieldname": "billed_amount",
				"fieldtype": "Currency",
				"width": 110,
				"options": "Company:company:default_currency",
				"convertible": "rate",
			},
			{
				"label": _("Pending Amount"),
				"fieldname": "pending_amount",
				"fieldtype": "Currency",
				"width": 130,
				"options": "Company:company:default_currency",
				"convertible": "rate",
			},
			{
				"label": _("Received Qty Amount"),
				"fieldname": "received_qty_amount",
				"fieldtype": "Currency",
				"width": 130,
				"options": "Company:company:default_currency",
				"convertible": "rate",
			},
			{
				"label": _("Warehouse"),
				"fieldname": "warehouse",
				"fieldtype": "Link",
				"options": "Warehouse",
				"width": 100,
			},
			{
				"label": _("Company"),
				"fieldname": "company",
				"fieldtype": "Link",
				"options": "Company",
				"width": 100,
			},
		]
	)

	return columns
