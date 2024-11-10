# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns =get_columns()
	data = get_data()
	return columns, data
def get_data():
    query = frappe.db.sql('''
        SELECT 
            name AS name,
            project AS project_name,
            wbs_name AS wbs_name,
            overall_budget AS amt_allocated,
            assigned_overall_budget AS amt_utilized,
            (overall_budget - assigned_overall_budget) AS amt_balanced,
            wbs_level AS wbs_level,
            CASE 
                WHEN overall_budget > 0 THEN (assigned_overall_budget / overall_budget) * 100
                ELSE 0
            END AS total_utilized,
            is_group,
            parent_work_breakdown_structure
        FROM `tabWork Breakdown Structure`
    ''', as_dict=True)

    wbs_map = {}
    for item in query:
        wbs_map.setdefault(item['parent_work_breakdown_structure'], []).append(item)

    tree_data = []

    for item in query:
        totals = {'amt_allocated': 0, 'amt_utilized': 0, 'amt_balanced': 0, 'total_utilized_percent': 0}
        if item['parent_work_breakdown_structure'] is None: 
            tree_data.append({
                'name': item['name'],
                'project_name': item['project_name'],
                'wbs_name': item['wbs_name'],
                'wbs_level': item['wbs_level'],
                'budget_period': 0,
                'amt_allocated': item['amt_allocated'],
                'amt_utilized': item['amt_utilized'],
                'amt_balanced': item['amt_balanced'],
                'total_utilized': item['total_utilized'],
                'indent': 0
            })
            
            totals['amt_allocated'] += item['amt_allocated']
            totals['amt_utilized'] += item['amt_utilized']
            totals['amt_balanced'] += item['amt_balanced']
            totals['total_utilized_percent'] += item['total_utilized']

            add_to_tree(item['name'], 1, wbs_map, tree_data, totals)

            tree_data.append({
                'wbs_name': 'Total',
                'amt_allocated': totals['amt_allocated'],
                'amt_utilized': totals['amt_utilized'],
                'amt_balanced': totals['amt_balanced'],
                'total_utilized': totals['total_utilized_percent'],
            })

    return tree_data

def add_to_tree(parent_id, indent, wbs_map, tree_data, totals):
    if parent_id in wbs_map:
        for child in wbs_map[parent_id]:
            tree_data.append({
                'name': child['name'],
                'project_name': child['project_name'],
                'wbs_name': child['wbs_name'],
                'wbs_level': child['wbs_level'],
                'budget_period': 0,
                'amt_allocated': child['amt_allocated'],
                'amt_utilized': child['amt_utilized'],
                'amt_balanced': child['amt_balanced'],
                'total_utilized': child['total_utilized'],
                'indent': indent
            })
            
            totals['amt_allocated'] += child['amt_allocated']
            totals['amt_utilized'] += child['amt_utilized']
            totals['amt_balanced'] += child['amt_balanced']
            totals['total_utilized_percent'] += child['total_utilized']

            add_to_tree(child['name'], indent + 1, wbs_map, tree_data, totals)
		
def get_columns():
	columns=[
			{
				"label": ("WBS Element"),
				"fieldname": "name",
				"fieldtype": "Link",
				"options": "Work Breakdown Structure",
				"width" : 250
			},
			{
				"label": ("WBS Name"),
				"fieldname": "wbs_name",
				"fieldtype": "Data",
			},
			{
				"label": ("WBS Level"),
				"fieldname": "wbs_level",
				"fieldtype": "Data",
			},
			{
				"label": ("Project Name"),
				"fieldname": "project_name",
				"fieldtype": "Link",
				"options": "Project",
			},
			{
				"label": ("Allocated Amount"),
				"fieldname": "amt_allocated",
				"fieldtype": "Float",
			},
			{
				"label": ("Utilized Amount"),
				"fieldname": "amt_utilized",
				"fieldtype": "Float",
			},
			{
				"label": ("Balanced Amount"),
				"fieldname": "amt_balanced",
				"fieldtype": "Float",
			},
			{
				"label": ("% Utilized"),
				"fieldname": "total_utilized",
				"fieldtype": "Float",
			}
	]

	return columns

