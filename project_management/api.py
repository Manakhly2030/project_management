import frappe, json
from frappe import _
from datetime import datetime ,timedelta
from erpnext.projects.doctype.project.project import Project,get_holiday_list
from frappe.utils import add_days
from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
@frappe.whitelist()
def get_tasks_from_multiple_template(name,tasks,parent_task=None,):
    try:
        tasks=json.loads(tasks)
        doc = frappe.get_doc("Project",name)
        project_tasks = []
        tmp_task_details = []
        
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
            task_doc.save()
            project_tasks.append(task_doc)
        doc.dependency_mapping(tmp_task_details, project_tasks)
        if len(project_tasks):
            return True
    except Exception as e:
        frappe.log_error(title="Get Tasks From Multiple Template",message=frappe.get_traceback())
        frappe.msgprint(_(str(e)))
    return False
@frappe.whitelist()
def get_task_value(template,project,as_per,company,custom_start_dates=None):
    as_per=int(as_per)
    tasks =frappe.get_all("Project Template Task",filters= { "parent": template }, fields= ["name",'task',"subject"])
    self=frappe.get_doc("Project",project)
    if custom_start_dates:

        custom_start_dates=json.loads(custom_start_dates)

        last_exp_date=custom_start_dates[0].get("start_date")
        if as_per==1:      
            for task in custom_start_dates:
                self.expected_start_date=last_exp_date
                task_start_duration=frappe.get_doc("Task",task.get("task"))
                if task["start_date"] > last_exp_date:
                    task ['start_date']=update_if_holiday(self,task ['start_date'])
                elif task["start_date"] < last_exp_date:
                    task ['start_date']=update_if_holiday(self,last_exp_date)
                self.start_date=task ['start_date']

                task["end_date"]=Project.calculate_end_date(self,task_start_duration)
                last_exp_date=add_days(task["end_date"],1)
        else:
            for task in custom_start_dates:
                self.expected_start_date=last_exp_date
                task_start_duration=frappe.get_doc("Task",task.get("task"))
                if task["start_date"] > last_exp_date:
                    task ['start_date']=update_if_holiday(self,task ['start_date'])
                elif task["start_date"] < last_exp_date:
                    task ['start_date']=update_if_holiday(self,last_exp_date)
                self.start_date=task ['start_date']
                task["end_date"]=task ['start_date']
                last_exp_date=add_days(task["end_date"],1)
       
        tasks =custom_start_dates


    else:
        last_exp_date=frappe.db.get_value("Task",{"project":project},"exp_end_date",order_by="creation")
        last_exp_date=add_days(last_exp_date, 1)
    

        if as_per==1:      
            for task in tasks:
                self.expected_start_date=last_exp_date
                task_start_duration=frappe.get_doc("Task",task.get("task"))
                task ['start_date']=Project.calculate_start_date(self,task_start_duration)
                task["end_date"]=Project.calculate_end_date(self,task_start_duration)
                last_exp_date=add_days(task["end_date"],1)
        else:
            for task in tasks:
                task ['start_date']=update_if_holiday(self,last_exp_date)
                task["end_date"]=task ['start_date']
                last_exp_date=add_days(task["end_date"],1)
    return tasks
def update_if_holiday(self, date):
    holiday_list = self.holiday_list or get_holiday_list(self.company)
    while is_holiday(holiday_list, date):
        date = add_days(date, 1)
    return date