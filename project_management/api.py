import frappe, json
from frappe import _
from datetime import datetime ,timedelta
from erpnext.projects.doctype.project.project import Project,get_holiday_list
from frappe.utils import add_days
from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
@frappe.whitelist()
def get_tasks_from_multiple_template(name,tasks,template,parent_task=None,from_task_tree=0):
	if from_task_tree:
		name=frappe.db.get_value("Task",name,"project")
	try:
		tasks=json.loads(tasks)
		doc = frappe.get_doc("Project",name)
		project_tasks = []
		tmp_task_details = []
		template_doc=frappe.get_doc("Project Template",template)
		for task in tasks:
			template_task_details = frappe.get_doc("Task", task.get("task"))
			tmp_task_details.append(template_task_details)
			task_doc = doc.create_task_from_template(template_task_details)
			if task.get("start_date"):
				task_doc.exp_start_date = task.get("start_date")
			if task.get("end_date"):
				task_doc.exp_end_date = task.get("end_date")                
			if parent_task:
				task_doc.parent_task=parent_task
			if template_task_details.get("expected_time"):
				task_doc.expected_time=template_task_details.get("expected_time")
			task_doc.save()
			get_all_child_task=creat_child_root_to_leaf(template_task_details,doc,task_doc)
			project_tasks.append(task_doc)
			project_tasks+get_all_child_task
		doc.dependency_mapping(tmp_task_details, project_tasks)
		if len(project_tasks):
			return True
	except Exception as e:
		frappe.log_error(title="Get Tasks From Multiple Template",message=frappe.get_traceback())
		frappe.msgprint(_(str(e)))
	return False
def creat_child_root_to_leaf(task_obj,doc,parent_doc):
	child_list=[]
	for task in task_obj.depends_on:
		task_doc=frappe.get_doc("Task",task.task)
		sub_doc=doc.create_task_from_template(task_doc)
		sub_doc.exp_start_date =None
		sub_doc.exp_end_date = None           
		sub_doc.parent_task=parent_doc.name
		if task_doc.get("expected_time"):
			sub_doc.expected_time= task_doc.get("expected_time")
		sub_doc.save()


		child_list.append(sub_doc)
		if task_doc.depends_on:
				child_list=child_list+creat_child_root_to_leaf(task_doc,doc,sub_doc)
	return child_list
@frappe.whitelist()
def get_task_value(template,project,company,custom_start_dates=None,as_per=0,from_task_tree=0):
	if from_task_tree:
		project,company=frappe.db.get_value("Task",project,["project","company"])
	as_per=int(as_per)
	tasks =frappe.get_all("Project Template Task",filters= { "parent": template }, fields= ["name",'task',"subject",])
	self=frappe.get_doc("Project",project)
	if custom_start_dates:

		custom_start_dates=json.loads(custom_start_dates)

		last_exp_date=custom_start_dates[0].get("start_date")
		if as_per==1:      
			for task in custom_start_dates:
				last_exp_date=task["start_date"]
				self.expected_start_date=last_exp_date
				task_start_duration=frappe.get_doc("Task",task.get("task"))
				task["expected_time"]=task_start_duration.expected_time
				if task["start_date"] > last_exp_date:
					task ['start_date']=update_if_holiday(self,task ['start_date'])
				elif task["start_date"] < last_exp_date:
					task ['start_date']=update_if_holiday(self,last_exp_date)
				self.start_date=task ['start_date']

				task["end_date"]=Project.calculate_end_date(self,task_start_duration)
			   
		else:
			for task in custom_start_dates:
				last_exp_date=task["start_date"]
				self.expected_start_date=last_exp_date
				task_start_duration=frappe.get_doc("Task",task.get("task"))
				task["expected_time"]=task_start_duration.expected_time
				task["type"]=task_start_duration.type
				if task["start_date"] > last_exp_date:
					task ['start_date']=update_if_holiday(self,task ['start_date'])
				elif task["start_date"] < last_exp_date:
					task ['start_date']=update_if_holiday(self,last_exp_date)
				self.start_date=task ['start_date']
				task["end_date"]=task ['start_date']
			   
	   
		tasks =custom_start_dates


	else:
		if as_per==1:      
			for task in tasks:
				last_exp_date=datetime.today()
				self.expected_start_date=last_exp_date
				task_start_duration=frappe.get_doc("Task",task.get("task"))
				task["expected_time"]=task_start_duration.expected_time
				task["type"] = task_start_duration.type
				task["is_group"]=task_start_duration.is_group
				task ['start_date']=Project.calculate_start_date(self,task_start_duration)
				task["end_date"]=Project.calculate_end_date(self,task_start_duration)
				
		else:
			for task in tasks:
				last_exp_date=datetime.today()
				task_start_duration=frappe.get_doc("Task",task.get("task"))
				task["expected_time"]=task_start_duration.expected_time
				task["type"]=task_start_duration.type
				task["is_group"] = task_start_duration.is_group
				task ['start_date']=update_if_holiday(self,last_exp_date)
				task["end_date"]=task ['start_date']
				
	return tasks
def update_if_holiday(self, date):
	if self.custom_customer_holiday_list:
		while is_holiday(self.custom_customer_holiday_list, date):
			date = add_days(date, 1)
	if self.holiday_list:
		while is_holiday(self.holiday_list, date):
			date = add_days(date, 1)
	elif get_holiday_list(self.company):
		while is_holiday ( get_holiday_list(self.company), date):
			date = add_days(date, 1)
	return date
def update_if_we_working_time(tasks,project):
	working_hours=frappe.db.get_value("Projects Settings","Projects Settings","custom_duration")
	for task in tasks:
		if task.task_type and frappe.db.get_value("Task Type",task.task_type,"custom_nature")=="Sequence":
			if working_hours:
				task_type_list=frappe.get_list("Task Type",fields=["name"],filters={"custom_nature":"Sequence"},pluck="name")
				filters={"project":project,
								"task_type":["in",task_type_list],
								
								"exp_start_date":task.start_date,
								"exp_end_date":task.start_date
								},
				filters2={"project":project,
								"task_type":["in",task_type_list],
							   
								"exp_start_date":task.start_date,
								"exp_end_date":["!=",task.start_date]
								},
				working_hours_per_project2=frappe.db.get_value("Task",filters2,"sum(expected_time)")
				
				working_hours_per_project=frappe.db.get_value("Task",filters,"sum(expected_time)")

@frappe.whitelist()
def fetch_task(template, parent_task, project):
	task_list = []
	next_start_date = ""
	project = frappe.get_doc("Project", project)
	task_template = frappe.get_doc("Project Template", template)
	working_hrs,from_time,to_time=get_all_working_times()
	from_time = datetime.strptime(from_time, "%H:%M:%S").time()
	to_time=datetime.strptime(to_time, "%H:%M:%S").time()
	start_date =  get_last_task_end_date(parent_task,from_time,to_time,project) 
	if not start_date:
		start_date =datetime.strptime(f"{project.expected_start_date} {from_time}", "%Y-%m-%d %H:%M:%S") if project.expected_start_date else None 
	if not start_date:
		start_date=datetime.combine(datetime.today(), from_time)

	start_date =update_if_holiday(project,start_date)
	for row in task_template.tasks:
		task = frappe.get_doc("Task", row.task)
		if (task.is_group and task.parent_task==None) or (task.is_group == 0 and task.parent_task==None) :
			start_date = next_start_date or start_date
			next_start_date = traverse_tasks_and_calculate_end_date(row.task, start_date,project)
			task_list.append({"task": row.task, "is_group": task.is_group, "type": task.type, "start_date": start_date, "end_date": next_start_date})
	return task_list
		

def get_last_task_end_date(parent_task,from_time,to_time,project):
	child_tasks = frappe.get_all('Task', filters={'parent_task': parent_task}, fields=['name', 'is_group', 'exp_end_date', 'creation'], order_by='creation')
	if not child_tasks:
		parent_task_doc = frappe.get_doc('Task', parent_task)
		return parent_task_doc.exp_start_date
	end_date=None
	for task in child_tasks:
		if task.is_group:
			end_date = get_last_task_end_date(task.name,from_time,to_time,project)
		else:
			if end_date:
				if task.exp_end_date and task.exp_end_date > end_date:
					end_date = task.exp_end_date
			else:
				end_date = task.exp_end_date
	if end_date:
		if end_date.time()<from_time:
			end_date=datetime.combine(end_date.date(),from_time)
		if end_date.time()>to_time:
			end_date=add_days(end_date,1)
			end_date =update_if_holiday(project,end_date)
	return end_date

def traverse_tasks_and_calculate_end_date(task, start_date,project):
	date_time_object = datetime.strptime(str(start_date), "%Y-%m-%d %H:%M:%S")
	task_list =  frappe.db.get_value("Task", task, ["expected_time"] ,as_dict=1)
	remaining_duration = timedelta(hours=task_list.get("expected_time"))
	time_intervals,from_time,to_time= get_all_working_times()
	end_date_time=None
	current_time=date_time_object.time()
	day_workin_hrs=timedelta(hours=get_working_hrs(date_time_object))
	from_time = datetime.strptime(from_time, "%H:%M:%S").time()
	to_time =datetime.strptime(to_time, "%H:%M:%S").time()
	datetime1 =date_time_object
	
	datetime2 = datetime.combine(date_time_object.date(), from_time)
	diff_in_hrs=(datetime1-datetime2)

	day_workin_hrs=day_workin_hrs -diff_in_hrs
	while remaining_duration > timedelta(0):
		if current_time < from_time:
			current_time=from_time
		if current_time > to_time:
			current_time=from_time
			date_time_object =add_days(date_time_object,1)
			date_time_object =update_if_holiday(project,date_time_object)
		if remaining_duration <= day_workin_hrs:
				end_date_time = date_time_object+remaining_duration
				return end_date_time
		else:
			remaining_duration =remaining_duration-day_workin_hrs
		date_time_object =add_days(date_time_object,1)
		date_time_object =update_if_holiday(project,date_time_object)
		date_time_object =datetime.combine(date_time_object.date(),from_time)
		current_time=date_time_object.time()
		day_workin_hrs=timedelta(hours=get_working_hrs(date_time_object))
	return None


def get_working_hrs(date):
	day_of_week = date.strftime("%A")
	working_hours=frappe.db.get_value("Project Working Time Table",{"parent":"Working Hour Template","day":day_of_week},"working_hours") or 0
	return working_hours
def get_all_working_times():
	working_hours=None
	from_time=None
	to_time=None
	try:
		working_hours=frappe.db.get_all("Project Working Time Table",{"parent":"Working Hour Template"},["working_hours","day"])
		from_time,to_time=frappe.db.get_value("Working Hour Template","Working Hour Template",["from_time","to_time"])
	except Exception as e:
		frappe.throw(str(e))
	return working_hours,from_time,to_time