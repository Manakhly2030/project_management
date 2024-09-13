import frappe
import math
from frappe.utils import (add_days,date_diff)
def task_overlapping(self,method):
	if self.type and frappe.db.get_value("Task Type",self.type,"custom_nature")=="Sequence" and self.is_template ==0:
		working_hours=frappe.db.get_value("Projects Settings","Projects Settings","custom_working_hours")
		working_hours=int(working_hours)/3600
		if working_hours:
			holiday_parent=frappe.db.get_value("Project",self.project,["holiday_list","custom_customer_holiday_list"],as_dict=1)
			holiday_paren_list=[holiday_parent.get("holiday_list"),holiday_parent.get("custom_customer_holiday_list")]
			validate_task(self,holiday_paren_list,working_hours)
			task_type_list=frappe.get_list("Task Type",fields=["name"],filters={"custom_nature":"Sequence"},pluck="name")
			filters={"project":self.project,
							"type":["in",task_type_list],
							"name":["not in",[self.name]],
							"status":["in",["Open","Working","Pending Review","Overdue"]],
							"expected_time":["!=",None]
							}
			filters_1={"exp_end_date":[">",self.exp_start_date]}
			filters_1.update(filters)
			already_working_task=frappe.db.get_value("Task",filters_1,["exp_end_date","name"],order_by="exp_end_date",as_dict=1)
			if already_working_task:
				frappe.throw("Task can not be added \n Task: " +str(already_working_task.get("name")) +" having End Date: "+str(already_working_task.get("exp_end_date")) +" Already Exists" )

			# filters_2={"exp_end_date":["=",self.exp_start_date],"exp_start_date":["!=",None]}
			# filters_2.update(filters)
			# already_working_task=frappe.db.get_list("Task",filters_2,["exp_start_date","exp_end_date","expected_time"])
			# avl_working_hours=working_hours
			# avl_already_working_task_working_hours=0
			# for taks_value in already_working_task:
			# 	avl_already_working_task_working_hours=avl_already_working_task_working_hours+get_total_working_hrs(taks_value.get("exp_start_date",taks_value.get("exp_end_date"),holiday_paren_list),working_hours) -taks_value.get("expected_time")
				
def get_total_working_hrs(from_date,to_date,holiday_paren_list,working_hours):
	no_of_days=get_no_of_working_days(from_date,to_date,holiday_paren_list)
	if no_of_days:
		return no_of_days*working_hours
	return working_hours
def get_no_of_working_days(from_date,to_date,holiday_paren_list):
	no_of_days=0
	no_of_days =((date_diff(to_date,from_date)+1) - get_no_of_holiday(from_date,to_date,holiday_paren_list)) or 0
	return no_of_days
def get_no_of_holiday(from_date,to_date,holiday_paren_list):
	count=0
	count =len(frappe.db.get_all("Holiday",{"holiday_date":["between", (from_date,to_date)] ,"parent":["in",holiday_paren_list]})) or 0
	return count
def validate_task(self,holiday_paren_list,working_hours):
	working_hours_as_task=get_total_working_hrs(self.exp_start_date,self.exp_end_date ,holiday_paren_list,working_hours)
	if working_hours_as_task< self.expected_time:
		frappe.throw("The Total working hours is: "+str(working_hours_as_task) +" as per  exp_start_date and exp_end_date but got "+str(self.expected_time) )
	no_of_days_of_work=working_hours_as_task /self.expected_time 
	if no_of_days_of_work >=2:
		frappe.msgprint("The exp_end_date can be reduced "+ str(int(no_of_days_of_work)))
def get_avl_working_hrs_sequence(date,working_hours,filters):
	start_date=date
	end_date=date
	custum_filters={}
	task_list=[]
	filters["exp_end_date"]=date
	
	end_date_task_list=frappe.db.get_list("Task",filters,["exp_start_date","exp_end_date","expected_time","name"])
	if len(end_date_task_list)>0:
		task_list=task_list+end_date_task_list
		for task  in end_date_task_list:
			filters["name"][1].append(task.get("name"))
			start_date_task_list=get_avl_working_hrs_sequence(task.get("exp_start_date"),working_hours,filters)
			if len(start_date_task_list)>0:
				task_list=task_list+start_date_task_list

	return task_list