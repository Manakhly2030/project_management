# Copyright (c) 2024, FRAPPE TECHNOLOGIES PRIVATE LIMITED and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	

	report_summary = get_report_summary(data,filters)
	return columns, data ,None,None,report_summary
def get_columns():
	columns = [
		
		{
			"label": _("Task"),
			"fieldtype": "Link",
			"fieldname": "name",
			"options":"Task",
			"bold":1,
			"width": 350,
		},
		
		{
			"label": _("Completion %"),
			"fieldtype": "Data",
			"fieldname": "progress",
			"width": 75,
		},
		{
			"label": _("Status"),
			"fieldtype": "Data",
			"fieldname": "status",
			"width": 75,
		},

		{
			"label": _("Expected Start"),
			"fieldtype": "Datetime",
			"fieldname": "exp_start_date",
			"width": 200,
		},
		{
			"label": _("Expected End"),
			"fieldtype": "Datetime",
			"fieldname": "exp_end_date",
			"width": 200,
		},
		{
			"label": _("Ageing"),
			"fieldtype": "Data",
			"fieldname": "ageing",
			"width": 75,

		},
		{
			"label": _("Estimated Hours"),
			"fieldtype": "Data",
			"fieldname": "expected_time",
			"width": 75,
		},
		{
			"label": _("Assignment"),
			"fieldtype": "Data",
			"fieldname": "_assign",
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
			"label": _("Project"),
			"fieldtype": "Link",
			"fieldname": "project",
			"options": "Project",
			"width": 150,
		},
		{
			"label": _("Task Type"),
			"fieldtype": "Link",
			"fieldname": "type",
			"options": "Task Type",
			"width": 150,
		},
		{
			"label": _("Action"),
			"fieldtype": "Data",
			"fieldname": "action",
			"width": 100,
		},
		{
			"label": _("Associated Documents"),
			"fieldtype": "Data",
			"fieldname": "associated_docname",
			"width": 150,
		}
	]
	return columns
def get_data(filters):
	project_f=filters.get("project")
	task_f =filters.get("task")
	from_date=filters.get("from_date")
	to_date=filters.get("to_date")
	company=filters.get("company")
	data=[]
	task_data=frappe.db.sql("""select 
							t.name,
							t.progress,
							t.exp_start_date,
							t.exp_end_date,
							t.act_start_date,
							t.act_end_date,
							t.status,
						 	t.type,
						 t.expected_time,
						 	 CAST(DATEDIFF(CURDATE(), t.exp_end_date)AS CHAR) as ageing,
						 	t.project,
						 	t.subject,
						 	tt.custom_is_action_required,
						 t.custom_expected_start_time,
							t.custom_expected_end_time,
						 t._assign,
						0.0 as indent
					from `tabTask`  as t
					left join `tabTask Type`as tt  on tt.name = t.type
					where 
							t.parent_task is Null
						 and
						 t.is_template=0
						 {0}
						 {1}
						 {2}
						 {3}
						 {4}
						 
							
							
			""".format((f"and  t.project ='{project_f}'"),
			  (f"and  t.company ='{company}'"),
			  (f"and t.name ='{task_f}'" if task_f else ''),											 
			f"  and t.exp_start_date is not Null and  t.exp_start_date != 0.0  and t.exp_start_date >= '{from_date}'  " if from_date else "",
				f"and t.exp_end_date is not Null  and t.exp_end_date !=0.0  and t.exp_end_date <= '{to_date} '" if to_date else "",
				
				),as_dict=1)
	for task in task_data:
		leaf_data=get_root_leaf_task(task.get("name"),1,filters)
		if leaf_data:
			task["bold"] =1
			task["progress"] = round(sum(progress.get("progress") or 0 for progress  in leaf_data )/len(leaf_data),2)
		else:
			task["bold"] =0
		data.append(task)
		data=data+leaf_data
	if filters.assign_to:
		new_data=[]
		for task in data:
			matched_assigned_user = [item for item in filters.assign_to if item in json.loads(task.get("_assign"))] if task.get("_assign") else []
			if matched_assigned_user:
				task._assign = matched_assigned_user
				new_data.append(task)
		data=new_data
	new_data=[]
	for task in data:
		if task.get("_assign"):
			if isinstance(task.get("_assign"), str):
				task["_assign"] = ",".join(json.loads(task.get("_assign")))
			else:
				task["_assign"] = ", ".join(task.get("_assign"))
		if task.get("custom_is_action_required"):
			action_v=(frappe.get_all("Document List",{"parent":task.get("type")},["document_type"],pluck="document_type",order_by ="is_default desc"))
			if action_v:
				if task.get("_assign") and( frappe.session.user in task["_assign"]):
					task["action"] = ",".join(action_v)
				task["show_action"] =",".join(action_v)
		
		
	return data
def get_root_leaf_task(task,indent,filters):
	project_f=filters.get("project")
	from_date=filters.get("from_date")
	to_date=filters.get("to_date")
	company=filters.get("company")
	ex_task_data=frappe.db.sql("""select 
								t.name,
								t.progress,
								t.exp_start_date,
								t.exp_end_date,
								t.act_start_date,
								t.act_end_date,
								t.project,
								t.status,
								t.type,
								t.subject,
								tt.custom_is_action_required,
							t.expected_time,
							t.custom_expected_start_time,
							t.custom_expected_end_time,
							t._assign,
							CAST(DATEDIFF(CURDATE(), t.exp_end_date)AS CHAR) as ageing,
							
							{0} as indent
						from `tabTask` as t
						left join `tabTask Type` as tt  on tt.name = t.type
						where t.parent_task = '{1}'
						and t.is_template=0
						{2}
						{3}
						{4}
						{5}
						
				""".format(indent,task,
			   
			f"  and t.exp_start_date is not Null and  t.exp_start_date !=0.0 and t.exp_start_date >= '{from_date}'  " if from_date else "",
				f"and t.exp_end_date is not Null  and t.exp_end_date !=0.0  and t.exp_end_date <= '{to_date} '" if to_date else "",
				f"and  company ='{company}'",
				f"and project = '{project_f}'"
				),as_dict=1)

	indent=indent+1
	data=[]
	for task_val in ex_task_data:
		leaf_data=get_root_leaf_task(task_val.get("name"),indent,filters)
		if leaf_data:
			task_val["bold"] =1
			task_val["progress"] = round(sum(progress.get("progress") or 0 for progress  in leaf_data )/len(leaf_data) ,2)
		else:
			task_val["bold"] =0

		data.append(task_val)
		data=data+leaf_data

	return data
def get_report_summary(data,filters):
	if not data:
		return None

	
	total = len(data)
	total_overdue = 0
	completed=0
	total_completion=0
	for task in  data:
		if task.get("status") =="Overdue":
			total_overdue=total_overdue+1
		elif task.get("status") == "Completed":
			completed=completed+1
		if task.get("progress"):
			total_completion=total_completion+float(task.get("progress"))
	avg_completion =frappe.db.get_value("Project",filters.get("project"),"percent_complete")



	return [
		{
			"value": avg_completion,
			"indicator": "Green" if avg_completion > 50 else "Red",
			"label": _("Average Completion"),
			"datatype": "Percent",
		},
		{
			"value": total,
			"indicator": "Blue",
			"label": _("Total"),
			"datatype": "Int",
		},
		{
			"value": completed,
			"indicator": "Green",
			"label": _("Completed"),
			"datatype": "Int",
		},
		{
			"value": total_overdue,
			"indicator": "Green" if total_overdue == 0 else "Red",
			"label": _("Overdue"),
			"datatype": "Int",
		},
	]
