# Copyright (c) 2024, FRAPPE TECHNOLOGIES PRIVATE LIMITED and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	

	report_summary = get_report_summary(data)
	print(data)
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
			"width": 150,
		},
		{
			"label": _("Expected End"),
			"fieldtype": "Datetime",
			"fieldname": "exp_end_date",
			"width": 150,
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
	]
	return columns
def get_data(filters):
	project_f=filters.get("project")
	task_f =filters.get("task")
	from_date=filters.get("from_date")
	to_date=filters.get("to_date")
	company=filters.get("company")
	my_task_user=None
	data=[]
	task_data=frappe.db.sql("""select 
							name,
							progress,
							exp_start_date,
							exp_end_date,
							act_start_date,
							act_end_date,
							status,
						 expected_time,
						 	 CAST(DATEDIFF(CURDATE(), exp_end_date)AS CHAR) as ageing,
						 	project,
						 	subject,
						 custom_expected_start_time,
							custom_expected_end_time,
						 _assign,
						0.0 as indent
					from `tabTask` 
				
					where 
							parent_task is Null
						 and
						 is_template=0
						 {0}
						 {1}
						 {2}
						 {3}
						 {4}
						 
							
							
			""".format((f"and  project ='{project_f}'"),
			  (f"and  company ='{company}'"),
			  (f"and name ='{task_f}'" if task_f else ''),											 
			f"  and exp_start_date is not Null and  exp_start_date != 0.0  and exp_start_date >= '{from_date}'  " if from_date else "",
				f"and exp_end_date is not Null  and exp_end_date !=0.0  and exp_end_date <= '{to_date} '" if to_date else "",

				),as_dict=1,debug=1)
	for task in task_data:
		leaf_data=get_root_leaf_task(task.get("name"),1,filters)
		if leaf_data:
			task["bold"] =1
			task["progress"] = sum(progress.get("progress") or 0 for progress  in leaf_data )/len(leaf_data)
		else:
			task["bold"] =0
		data.append(task)
		data=data+leaf_data
	if not project_f:
		task_data=frappe.db.sql("""select 
								name,
								progress,
								exp_start_date,
								exp_end_date,
								act_start_date,
								act_end_date,
						  expected_time,
								status,
						  		subject,
						  custom_expected_start_time,
							custom_expected_end_time,
						  _assign,
						 CAST(DATEDIFF(exp_end_date,CURDATE())AS CHAR) as ageing,
							0.0 as indent
						from `tabTask` 
					
						where 
								parent_task is Null
						  		and is_template=0
								and project is Null
								{0}
								{1}
						  		{2}
						  		{3}
								
				""".format(
					(f"and name ='{task_f}'" if task_f else ''),
					f"and  company ='{company}'",
				f"  and exp_start_date is not Null and  exp_start_date !=0.0 and exp_start_date >= '{from_date}'  " if from_date else "",
				f"and exp_end_date is not Null  and exp_end_date !=0.0  and exp_end_date <= '{to_date} '" if to_date else "",
				),as_dict=1,debug=1)
		for task in task_data:
			leaf_data=get_root_leaf_task(task.get("name"),1,filters)
			if leaf_data:
				task["bold"] =1
				task["progress"] = sum(progress.get("progress") or 0 for progress  in leaf_data )/len(leaf_data)
			else:
				task["bold"] =0
			
			data.append(task)

			data=data+leaf_data
	if filters.show_my_tasks==1:
		new_data=[]
		for task in data:
			user = frappe.session.user
			print("_assign",task.get("_assign"))
			if task.get("_assign") and  user in json.loads(task.get("_assign")):
				print(json.loads(task.get("_assign")))
				new_data.append(task)
		data=new_data
	for task in data:
		if task.get("_assign"):
			task["_assign"] = ",".join(json.loads(task.get("_assign")))
		if task.get("custom_expected_start_time") and  task.get("exp_start_date"):
			task["exp_start_date"] = str(task["exp_start_date"])+ " "+ str(task.get("custom_expected_start_time"))
		if task.get("custom_expected_end_time") and task.get("exp_end_date"):
			task["exp_end_date"] = str(task["exp_end_date"])+" "+str(task.get("custom_expected_end_time"))
	return data
def get_root_leaf_task(task,indent,filters):
	from_date=filters.get("from_date")
	to_date=filters.get("to_date")
	company=filters.get("company")
	my_task_user=frappe.session.user_email if filters.get("show_my_tasks") else None
	ex_task_data=frappe.db.sql("""select 
								name,
								progress,
								exp_start_date,
								exp_end_date,
								act_start_date,
								act_end_date,
								status,
								subject,
							expected_time,
							custom_expected_start_time,
							custom_expected_end_time,
							_assign,
							CAST(DATEDIFF(CURDATE(), exp_end_date)AS CHAR) as ageing,
							
							{0} as indent
						from `tabTask` 
						where parent_task = '{1}'
						and is_template=0
						{2}
						{3}
						{4}
						
						
				""".format(indent,task,
			   
			f"  and exp_start_date is not Null and  exp_start_date !=0.0 and exp_start_date >= '{from_date}'  " if from_date else "",
				f"and exp_end_date is not Null  and exp_end_date !=0.0  and exp_end_date <= '{to_date} '" if to_date else "",
				f"and  company ='{company}'"
				),as_dict=1,debug=1)

	indent=indent+1
	data=[]
	for task_val in ex_task_data:
		leaf_data=get_root_leaf_task(task_val.get("name"),indent,filters)
		if leaf_data:
			task_val["bold"] =1
			task_val["progress"] = sum(progress.get("progress") or 0 for progress  in leaf_data )/len(leaf_data)
		else:
			task_val["bold"] =0

		data.append(task_val)
		data=data+leaf_data

	return data
def get_report_summary(data):
	if not data:
		return None

	
	total = len(data)
	total_overdue = 0
	completed=0
	for task in  data:
		if task.get("status") =="Overdue":
			total_overdue=total_overdue+1
		elif task.get("status") == "Completed":
			completed=completed+1
	avg_completion =completed / total



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
			"label": _("Total Tasks"),
			"datatype": "Int",
		},
		{
			"value": completed,
			"indicator": "Green",
			"label": _("Completed Tasks"),
			"datatype": "Int",
		},
		{
			"value": total_overdue,
			"indicator": "Green" if total_overdue == 0 else "Red",
			"label": _("Overdue Tasks"),
			"datatype": "Int",
		},
	]
