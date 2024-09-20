// Copyright (c) 2024, FRAPPE TECHNOLOGIES PRIVATE LIMITED and contributors
// For license information, please see license.txt

frappe.query_reports["Project Task Summary"] = {
	"filters": [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options:"Company",
			reqd: 1,
			
			
		},
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options:"Project",
			reqd: 1,
			get_query: () => {
				var company = frappe.query_report.get_filter_value("company");
				if (company){
					return {
						filters: {
							company: company,
						},
					};
				}
			},
			
			
		},
		{
			
				fieldname: "from_date",
				label: __("From Date"),
				fieldtype: "Date"

		},
		{
			
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
		},
		{
			label: "Timespan",
			fieldtype: "Select",
			fieldname: "timespan",
			options: [
				"Last Week",
				"Last Month",
				"Last Quarter",
				"Last 6 months",
				"Last Year",
				"This Week",
				"This Month",
				"This Quarter",
				"This Year",
			],
			on_change: function () {
				let timespan = company = frappe.query_report.get_filter_value("timespan").toLowerCase();
				let current_date = frappe.datetime.now_date();
				let date_range_map = {
			"this week": [frappe.datetime.week_start(), frappe.datetime.week_end()],
			"this month": [frappe.datetime.month_start(), frappe.datetime.month_end()],
			"this quarter": [frappe.datetime.quarter_start(), frappe.datetime.quarter_end()],
			"this year": [frappe.datetime.year_start(), frappe.datetime.year_end()],
			"last week": [frappe.datetime.add_days(current_date, -7), current_date],
			"last month": [frappe.datetime.add_months(current_date, -1), current_date],
			"last quarter": [frappe.datetime.add_months(current_date, -3), current_date],
			"last year": [frappe.datetime.add_months(current_date, -12), current_date],
			"last 6 months": [frappe.datetime.add_months(current_date, -6), current_date]
		};
		frappe.query_report.set_filter_value("from_date", date_range_map[timespan][0]);
		frappe.query_report.set_filter_value("to_date", date_range_map[timespan][1]);

			}
			
		},
		{
			fieldtype: "MultiSelectPills",
			fieldname: "assign_to",
			label: __("Assign To"),
			get_data: function (txt) {
				return frappe.db.get_link_options("User", txt, {
					enabled: 1,
				});
			},
		},
		
		
	],
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if(value){
		if (column["fieldname"] =="name"){
			value = `<a href="/app/task/${data["name"]}" data-doctype="Task" data-name="${data["name"]}" data-value="${data["name"]}">${data["name"]}:${data["subject"]}</a>`
			}
		
		if (data["bold"] ==1) {
			value=((value.toString()).bold())
		}
		if (column["fieldname"] =="status" || column["fieldname"] == "ageing")
		{
		
				

				if ( data["status"] == "Open" ||data["status"] == "Working" ||data["status"] == "Pending Review" )
				{
					value=`<span style='color:orange'>${value}</span>`
	
				}
				else if ( data["status"] == "Overdue" || data["status"] ==  "Cancelled")
					{

						value=`<span style='color:red'>${value}</span>`
					}
				
				else if (data["status"] == "Completed")
				{
					value=`<span style='color:green'>${value}</span>`
				}

					
			

		}
		
	}
	if (column["fieldname"] == "action"){
		
		if (value){
			var task_name=data["name"]
			value = `<button class="btn btn-default btn-xs" style=" cursor: pointer" onclick="frappe.query_reports['Project Task Summary'].creat_action('${value}','${task_name}')">Action</button>`;
			
		}
		else{
		value =""
		}

	}
	if (column["fieldname"] == "associated_docname"){
		if (data["action"]){
			var dt=data["action"]
			var task_f=data["name"]
			value = `<button class="btn btn-default btn-xs" style=" cursor: pointer" onclick="frappe.query_reports['Project Task Summary'].show_list('${dt}','${task_f}')">Show</button>`;

		}
		else{
			value = ""
		}

	}
		return value;
	},
	onload(report) {
		report.page.add_inner_button(__("Gantt chart"), () => {
			company=frappe.query_report.get_filter_value("company")
			project=frappe.query_report.get_filter_value("project")
			show_my_tasks=frappe.query_report.get_filter_value("show_my_tasks") 
			from_date=frappe.query_report.get_filter_value("from_date") 
			to_date=frappe.query_report.get_filter_value("to_date") 
			frappe.open_in_new_tab = true;
			if (show_my_tasks){
				show_my_tasks=frappe.session.user
				frappe.set_route(['List', 'Task', 'Gantt',{"company":company,"project":project,
					"_assign":["like", "%" +show_my_tasks  + "%"] ,
					"exp_start_date":[">=",from_date],
					"exp_end_date":["<=",to_date]
   
				}])
			}
			else{
				frappe.set_route(['List', 'Task', 'Gantt',{"company":company,"project":project,
					"exp_start_date":[">=",from_date],
					"exp_end_date":["<=",to_date]
   
				}])

			}

		})
	},
	creat_action:function(value,task_name){
		
		var value=value.split(",")
		if (value.length>1){
		var d = new frappe.ui.Dialog({
			title: __("Select The Document Type"),
			fields: [
				{
					label: "Document Type",
					fieldname: "documents",
					fieldtype: "Select",
					reqd: 1,
					options:value.join("\n"),
					default:value[0]
				},
			],
			primary_action: function () {
				debugger
				var data = d.get_values();
				value=data.documents
				value=(value.toLowerCase()).replaceAll(" ", "-");
				console.log(value)
				window.open(`/app/${value}/new-${value}-new?task=${task_name}&project=${frappe.query_report.get_filter_value("project")}`, "_blank");
			},
			primary_action_label: __("Create"),

		})
		d.show()
	}
	else{
		value=value[0]
		if (value){
			debugger
			console.log(value)
			value=(value.toLowerCase()).replaceAll(" ", "-");
			console.log(value)
			window.open(`/app/${value}/new-${value}-new?task=${task_name}`, "_blank");
		}
	}
		
		
	},
	show_list:function(doctype,task_name)
	{
		var value=doctype.split(",")
		if (value.length>1){
		var d = new frappe.ui.Dialog({
			title: __("Select The Document Type"),
			fields: [
				{
					label: "Documents",
					fieldname: "documents",
					fieldtype: "Select",
					reqd: 1,
					options:value.join("\n"),
					default:value[0]
				},
			],
			primary_action: function () {
				var data = d.get_values();
				value=data.documents
				frappe.open_in_new_tab = true;
				frappe.set_route(['List',value,{task:task_name}])
			},
			primary_action_label: __("Show"),

		})
		d.show()
	}
	else{
		value=value[0]
		if (value){
			frappe.open_in_new_tab = true;
			frappe.set_route(['List',value,{task:task_name}])
		}
	}
		

	}
};
