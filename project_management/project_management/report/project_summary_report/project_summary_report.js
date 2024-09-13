// Copyright (c) 2024, FRAPPE TECHNOLOGIES PRIVATE LIMITED and contributors
// For license information, please see license.txt

frappe.query_reports["Project Summary Report"] = {
	"filters": [
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options:"Project",
		},
		{
			fieldname: "task",
			label: __("Task"),
			fieldtype: "Link",
			options:"Task",
			get_query: () => {
				var project = frappe.query_report.get_filter_value("project");
				if (project){
					return {
						filters: {
							project: project,
						},
					};
				}
			},
			
		}
		
	]
};
