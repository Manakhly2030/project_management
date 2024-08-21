import frappe, json

@frappe.whitelist()
def get_tasks_from_multiple_template(template, name):
    if template:
        doc = frappe.get_doc("Project",frappe.form_dict.name)
        template_list = [name.lstrip().rstrip() for name in json.loads(template)["template"].split(",")]
        project_tasks = []
        tmp_task_details = []
        for name in template_list:
            if not name or name == " ":
                continue
            template = frappe.get_doc("Project Template", name)
            for task in template.tasks:
                template_task_details = frappe.get_doc("Task", task.task)
                tmp_task_details.append(template_task_details)
                task = doc.create_task_from_template(template_task_details)
                project_tasks.append(task)
        doc.dependency_mapping(tmp_task_details, project_tasks)
        if len(project_tasks):
            return True
        return False