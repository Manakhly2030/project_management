import frappe, json
from frappe import _
from datetime import datetime ,timedelta
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
            print(template_task_details.__dict__)
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
def get_task_value(template,project,company):
    last_exp_date=frappe.db.get_value("Task",{"project":project},"exp_start_date",order_by="creation")
    
    
    tasks =frappe.get_all("Project Template Task",filters= { "parent": template }, fields= ["name",'task',"subject"])
    for task in tasks:
        last_exp_date=next_woking_date(last_exp_date,company)
        task ['start_date']=str(last_exp_date)
        task["end_date"]=str(last_exp_date)
    return tasks
@frappe.whitelist()
def next_woking_date(date,company):
    exp_start_date = datetime.strptime(str(date), '%Y-%m-%d')  if str(type(date)) =="<class 'datetime.date'>" else datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S')
    exp_start_date = exp_start_date + timedelta(days=1)
    today = datetime.today()
    if exp_start_date < today:
        exp_start_date = today
    default_holiday_list=frappe.db.get_value("Company",company,"default_holiday_list")
    if default_holiday_list:
        to_date=frappe.db.get_value("Holiday List",default_holiday_list,"to_date")
        to_date=datetime.strptime(str(to_date), '%Y-%m-%d')
        if to_date >= exp_start_date:
            leave_date=frappe.get_all("Holiday",{"parent":default_holiday_list},"holiday_date",pluck="holiday_date")
            if len(leave_date):
                while True:
                    if exp_start_date in leave_date:
                        exp_start_date = exp_start_date + timedelta(days=1)
                    else:
                        break
        else:
            frappe.throw("Default holiday Not in range for  Company  "+company +" \n got date "+str(exp_start_date))
    else:
        frappe.throw("Please set default holiday list in Company "+company)
    return exp_start_date 