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
			"label": _("Project"),
			"fieldtype": "Link",
			"fieldname": "project",
			"options": "Project",
			"width": 150,
		},
		
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
	]
	return columns
def get_data(filters):
	project_f=filters.get("project")
	task_f =filters.get("task")
	project_data=frappe.db.sql("""select 
					name as project,
					expected_start_date as exp_start_date,
					expected_end_date as exp_end_date,
					actual_start_date as act_start_date,
					actual_end_date as act_end_date,
					percent_complete as progress,
					status,
					0.0 as indent
					from `tabProject`
					{0}
		""".format(f"where name ='{project_f}'" if project_f else ""),as_dict=1)
	data=[]
	for project in project_data:
		data.append(project)
		task_data=frappe.db.sql("""select 
								name,
								progress
								exp_start_date,
								exp_end_date,
								act_start_date,
								act_end_date,
								status,
							1.0 as indent
						from `tabTask` 
					
						where 
								parent_task is Null
						  		and project = '{0}'
						  		{1}
								
								
				""".format(project.get("project"),(f"and name ='{task_f}'" if task_f else '')),as_dict=1)
		print(task_data)
		for task in task_data:
			data.append(task)
			data=data+get_root_leaf_task(task.get("name"),2)
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
						  		{1}
								
								
				""".format(project.get("project"),(f"and name ='{task_f}'" if task_f else '')),as_dict=1)
		print(task_data)
		for task in task_data:
			data.append(task)
			data=data+get_root_leaf_task(task.get("name"),1)
	return data
def get_root_leaf_task(task,indent):
	print(task)
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
	print(task_data)
	return task_data