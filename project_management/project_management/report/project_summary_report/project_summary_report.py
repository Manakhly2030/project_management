# Copyright (c) 2024, FRAPPE TECHNOLOGIES PRIVATE LIMITED and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data
def get_columns():
	columns = [
		
		{
			"label": _("Task"),
			"fieldtype": "Link",
			"fieldname": "name",
			"options": "Task",
			"width": 300,
		},
		
		{
			"label": _("Completion %"),
			"fieldtype": "Data",
			"fieldname": "progress",
			"width": 150,
		},
		{
			"label": _("Expected Start"),
			"fieldtype": "Date",
			"fieldname": "exp_start_date",
			"width": 150,
		},
		{
			"label": _("Expected End"),
			"fieldtype": "Date",
			"fieldname": "exp_end_date",
			"width": 150,
		},
		{
			"label": _("Actual Start"),
			"fieldtype": "Date",
			"fieldname": "act_start_date",
			"width": 150,
		},
		{
			"label": _("Actual End"),
			"fieldtype": "Date",
			"fieldname": "act_end_date",
			"width": 150,
		},
		{
			"label": _("Status"),
			"fieldtype": "Data",
			"fieldname": "status",
			"width": 75,
		},
		{
			"label": _("Project"),
			"fieldtype": "Link",
			"fieldname": "project",
			"options": "Project",
			"width": 150,
		},
	]
	return columns
def get_data(filters):
	project_f=filters.get("project")
	task_f =filters.get("task")
	data=[]
	task_data=frappe.db.sql("""select 
							name,
							progress
							exp_start_date,
							exp_end_date,
							act_start_date,
							act_end_date,
							status,
						 	project,
						0.0 as indent
					from `tabTask` 
				
					where 
							parent_task is Null
							{0}
							{1}
							
							
			""".format((f"and  project ='{project_f}'" if project_f else ""),(f"and name ='{task_f}'" if task_f else '')),as_dict=1)
	for task in task_data:
		data.append(task)
		data=data+get_root_leaf_task(task.get("name"),1)
	if not project_f:
		task_data=frappe.db.sql("""select 
								name,
								progress
								exp_start_date,
								exp_end_date,
								act_start_date,
								act_end_date,
								status,
							0.0 as indent
						from `tabTask` 
					
						where 
								parent_task is Null
								and project is Null
								{0}
								
								
				""".format((f"and name ='{task_f}'" if task_f else '')),as_dict=1)
		for task in task_data:
			data.append(task)
			data=data+get_root_leaf_task(task.get("name"),1)
	return data
def get_root_leaf_task(task,indent):

	task_data=frappe.db.sql(f"""select 
								name,
								progress,
								exp_start_date,
								exp_end_date,
								act_start_date,
								act_end_date,
								status,
							{indent} as indent
						from `tabTask` 
						where parent_task = '{task}'
				""",as_dict=1)
	
	indent=indent+1
	for task_val in task_data:
		task_data=task_data+get_root_leaf_task(task_val.get("name"),indent)

	return task_data