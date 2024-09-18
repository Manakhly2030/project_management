import frappe
import math
from datetime import datetime,timedelta
from frappe.utils import (add_days,date_diff)
from erpnext.projects.doctype.project.project import get_holiday_list
from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
from project_management.api import update_if_holiday
def task_overlapping(self,method):
	try:
		if validate_task_timing_sequence_task(self):
			exp_start_date=datetime.now()
			exp_end_date=datetime.now()
			if self.exp_start_date:
				if len(str(self.exp_start_date)) ==26:
					self.exp_start_date = str(self.exp_start_date[:-7])
				exp_start_date=datetime.strptime(str(self.exp_start_date), "%Y-%m-%d %H:%M:%S")
			if self.exp_end_date:
				if len(str(self.exp_end_date)) ==26:
					self.exp_end_date = str(self.exp_end_date[:-7])
				exp_end_date=datetime.strptime(str(self.exp_end_date), "%Y-%m-%d %H:%M:%S")

			filters=get_common_sequence_filters(self.project,self.name)
			project_doc=frappe.get_doc("Project",self.project)

			check_in_between(self,filters,project_doc)
			already_working_task=check_in_same_date(self,filters)
			if already_working_task:
				avl_working_hrs_with_data=is_avl_to_start_on_with_data(exp_start_date.date(),already_working_task)
				if avl_working_hrs_with_data.get("avl_hours"):
					self.custom_expected_start_time =avl_working_hrs_with_data.get("next_start_time")
					
					self.exp_start_date = str(exp_start_date.date())+" "+str(avl_working_hrs_with_data.get("next_start_time"))

					end_date, end_time=get_end_data_time(exp_start_date.date(),avl_working_hrs_with_data.get("next_start_time"),self.expected_time,project_doc)
					if end_date:
						self.exp_end_date =str(end_date)+" "+str(end_time)
						if end_time:
							self.custom_expected_end_time=end_time
							push_tasks(self)
							
				else:
					frappe.log_error(title="exp_start_date Can not be "+str(self.exp_start_date),reference_doctype="Task",reference_name=self.name)
					
					exp_start_date=add_days(self.exp_start_date,1)
					exp_start_date =update_if_holiday(project_doc,exp_start_date)
					self.exp_start_date =str(exp_start_date)
					return task_overlapping(self,"Validate")
			else:
				custom_expected_start_time=get_working_start_times()
				if custom_expected_start_time:
					self.custom_expected_start_time=custom_expected_start_time[0]
					self.exp_start_date = str(exp_start_date.date())+" "+str(custom_expected_start_time[0])
					end_date, end_time=get_end_data_time(exp_start_date.date(),self.custom_expected_start_time,self.expected_time,project_doc)
					if end_date:
						self.exp_end_date =str(end_date)+" "+str(end_time)
						if end_time:
							self.custom_expected_end_time=end_time
							push_tasks(self)
	except Exception as e:
		frappe.log_error(title="task_overlapping",reference_doctype="Task",message=frappe.get_traceback(with_context=True),reference_name=self.name)


def push_tasks(self):
	filters=get_common_sequence_filters(self.project,self.name)
	check_and_push(self,filters)
def check_and_push(self,filters):
	filters["exp_end_date"]=[">=",self.exp_end_date]
	filters["exp_start_date"]=["<=",self.exp_end_date]
	already_working_tasks=frappe.db.get_list("Task",filters,["name"],pluck="name",order_by="custom_expected_end_time desc")
	for task in already_working_tasks:
		task_doc=frappe.get_doc("Task",task)
		task_doc.save()
def get_end_data_time(start_date,start_time,expected_time,project_doc):
	if not expected_time:
		expected_time=0
	remaining_duration = timedelta(hours=expected_time)
	current_time = start_time
	current_date = add_days(start_date,0)
	time_intervals= get_all_working_times()
	while remaining_duration > timedelta(0):
		for interval in time_intervals:
			from_time = interval['from_time']
			to_time = interval['to_time']
			if from_time <= current_time < to_time:
				remaining_time_in_interval = to_time - current_time
				if remaining_duration <= remaining_time_in_interval:
					end_time = current_time + remaining_duration
					return current_date, end_time
				else:
					remaining_duration -= remaining_time_in_interval
					current_time = to_time
			elif current_time < from_time:
				current_time = from_time
				remaining_time_in_interval = to_time - current_time

				if remaining_duration <= remaining_time_in_interval:
					return current_date, current_time + remaining_duration
				else:
					remaining_duration -= remaining_time_in_interval
					current_time = to_time
		current_date =add_days(current_date,1)
		current_date =update_if_holiday(project_doc,current_date)
		current_time = timedelta(seconds=0)
	return None, None

def validate_task_timing_sequence_task(self):
	if is_sequence_task(self.type,self.name,self.is_template):
		# working_hours_as_task=get_total_working_hrs(self)
		# if working_hours_as_task< self.expected_time:
		# 	frappe.throw("The Total working hours is: "+str(working_hours_as_task) +" as per  exp_start_date and exp_end_date but got "+str(self.expected_time) )
		return True
	return False

def get_total_working_hrs(self):
	working_hours =get_working_hours()
	holiday_paren_list=get_all_hoiday_list_as_per_project(self.project,self.company)
	no_of_days=get_no_of_working_days(self.exp_start_date,self.exp_end_date,holiday_paren_list)
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

def check_sequence_type(type,name):
	is_sequence=False
	try:
		if (frappe.db.get_value("Task Type",type,"custom_nature")=="Sequence"):
			is_sequence=True

	except Exception as e:
		frappe.log_error(title="Task Type Nature",message=frappe.get_traceback(with_context=True),reference_doctype="Task",reference_name=name)
	return is_sequence
def is_sequence_task(type,name,is_template):
	is_validate_sequence=False
	try:
		if type and check_sequence_type(type,name) and is_template==0:
			is_validate_sequence=True
	except Exception as e:
		frappe.log_error(title="Check Validate Task",message=frappe.get_traceback(with_context=True),reference_doctype="Task",reference_name=name)

	return is_validate_sequence
def get_working_hours():
	working_hours=0
	working_hours=frappe.db.get_value("Projects Settings","Projects Settings","custom_working_hours")
	if working_hours:
		working_hours=int(working_hours)/3600
	else:
		frappe.throw("Set Working Hours in Projects Setting")
	return working_hours
def get_all_hoiday_list_as_per_project(project,company=None,add_customer_holiday=1):
	holiday_paren_list=[]
	try:
		holiday_parent=frappe.db.get_value("Project",project,["holiday_list","custom_customer_holiday_list"],as_dict=1)
		if holiday_parent.get("holiday_list"):
			holiday_paren_list.append(holiday_parent.get("holiday_list")) 
		else:
			company_holiday_list=get_holiday_list(company)
			if company_holiday_list:
				holiday_paren_list.append(company_holiday_list)
		if add_customer_holiday:
			if holiday_parent.get("custom_customer_holiday_list"):
				holiday_paren_list.append(holiday_parent.get("custom_customer_holiday_list"))
	except Exception as e:
		frappe.log_error(title="Get Hoiday List",message=frappe.get_traceback(with_context=True),reference_doctype="Project",reference_name=project)
	return holiday_paren_list
def get_common_sequence_filters(project,name):
		filters={}
		try:
			task_type_list=get_sequence_task_type()
			filters={"project":project,
							"type":["in",task_type_list],
							"name":["not in",[name]],
							"status":["in",["Open","Working","Pending Review","Overdue"]]
							}
		except Exception as e:
			frappe.log_error(title="Get Common Sequence Filters",message=frappe.get_traceback(with_context=True))
		
		return filters
def get_sequence_task_type():
	task_type_list=[]
	try:
		task_type_list=frappe.get_list("Task Type",fields=["name"],filters={"custom_nature":"Sequence"},pluck="name")
	except Exception as e:
		frappe.log_error(title="Get Sequence Task Type",message=frappe.get_traceback(with_context=True))
	return task_type_list
def check_in_between(self,filters,project_doc):
	filters["exp_end_date"]=[">",self.exp_start_date]
	filters["exp_start_date"]=["<=",self.exp_start_date]
	already_working_task=frappe.db.get_value("Task",filters,["exp_end_date","name"],order_by="exp_end_date",as_dict=1)
	if already_working_task:
		
		frappe.log_error(title="exp_start_date Can not be "+str(self.exp_start_date),reference_doctype="Task",reference_name=self.name)
		exp_start_date=add_days(self.exp_start_date,1)
		exp_start_date =update_if_holiday(project_doc,exp_start_date)
		self.exp_start_date =str(exp_start_date)
		return task_overlapping(self,"Validate")
		
def check_in_same_date(self,filters):
		already_working_task=[]
		filters["exp_end_date"]=self.exp_start_date
		already_working_task=frappe.db.get_value("Task",filters,["exp_start_date","exp_end_date","expected_time","custom_expected_start_time","custom_expected_end_time","name"],as_dict=1,order_by="custom_expected_end_time desc")
		return already_working_task
def is_avl_to_start_on_with_data(date,task,working_hours=None):
	avl_hours=timedelta(0)
	if not working_hours:
		working_hours=get_working_hours()
		working_hours=timedelta(hours=working_hours)
	end_time=task.get("custom_expected_end_time")
	worked_hours_next_statime =find_worked_hours_next_start_time_with_end_time(end_time)
	avl_hours=working_hours - worked_hours_next_statime.get("worked_hours")
	return {"avl_hours":avl_hours,
		 "worked_hours":worked_hours_next_statime.get("worked_hours"),
		 "next_start_time":worked_hours_next_statime.get("next_start_time")}

def find_worked_hours_next_start_time_with_end_time(end_time):
		
		worked_hours= timedelta(0)
		all_working_interval=get_all_working_times()
		for interval in all_working_interval:
			from_time=interval.get("from_time")
			to_time=interval.get("to_time")
			if interval.get("from_time")<= end_time<=interval.get("to_time"):
				worked_hours =worked_hours +(from_time -end_time)
			else:
				worked_hours =worked_hours+(to_time - from_time)
		if worked_hours:
			worked_hours/3600
		return {"worked_hours":worked_hours,"next_start_time":end_time}




def get_all_working_times():
	get_all_working_times=[]
	try:
		get_all_working_times=frappe.db.get_all("Project working Time Table",{"parent":"Projects Settings"},["from_time","to_time"],order_by="from_time")
	except Exception as e:
		frappe.log_error(title="Get All Working Time",message=frappe.get_traceback(with_context=True))
	return get_all_working_times
def get_working_end_times():
	end_time_list=[]
	try:
		end_time_list=frappe.db.get_all("Project working Time Table",{"parent":"Projects Settings"},"to_time",pluck="to_time")
		if end_time_list:
			end_time_list=sorted(end_time_list)
	except Exception as e:
		frappe.log_error(title="Get Working End Time",message=frappe.get_traceback(with_context=True))
	return end_time_list
def get_working_start_times():
	start_time_list=0
	try:
		start_time_list=frappe.db.get_all("Project working Time Table",{"parent":"Projects Settings"},"from_time",pluck="from_time")
		if start_time_list:
			start_time_list=sorted(start_time_list)
	except Exception as e:
		frappe.log_error(title="Get Working Start Time",message=frappe.get_traceback(with_context=True))
	return start_time_list