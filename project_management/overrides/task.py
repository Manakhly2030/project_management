import frappe
def task_overlapping(self,method):
    if self.task_type and frappe.db.get_value("Task Type",self.task_type,"custom_nature")=="Sequence":
        working_hours=frappe.db.get_value("Projects Settings","Projects Settings","custom_duration")
        if working_hours:
            task_type_list=frappe.get_list("Task Type",fields=["name"],filters={"custom_nature":"Sequence"},pluck="name")
            filters={"project":self.project,
                            "task_type":["in",task_type_list],
                            "name":["!=",self.name],
                            "exp_start_date":self.exp_start_date,
                            "exp_end_date":self.exp_start_date
                            },
            working_hours_per_project=frappe.db.get_value("Task",filters,"sum(expected_time)")

            if (working_hours -working_hours_per_project) < self.expected_time:
                task_list = frappe.get_list("Task",
                        fields=["name"],
                        filters=filters,
                        pluck="name")
                for task in task_list:
                    task_doc=frappe.get_doc("Task",task)
            