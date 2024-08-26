import frappe, json
from frappe import _
@frappe.whitelist()
def get_tasks_from_multiple_template(template,name,parent_task=None):
    try:
        doc = frappe.get_doc("Project",name)
        project_tasks = []
        tmp_task_details = []
        tasks =frappe.get_all("Project Template Task",filters= { "parent": template }, fields= 'task',pluck="task")
        for task in tasks:
            template_task_details = frappe.get_doc("Task", task)
            tmp_task_details.append(template_task_details)
            task_doc = doc.create_task_from_template(template_task_details)
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