// Copyright (c) 2024, FRAPPE TECHNOLOGIES PRIVATE LIMITED and contributors
// For license information, please see license.txt

frappe.query_reports["Task Summary"] = {
	
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
			
			fieldname: "show_my_tasks",
			label: __("Show my tasks"),
			fieldtype: "Check",
		},
		
		
	],
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if(value){
		if (column["fieldname"] =="name"){
			value = `<a href="/app/task/${data["name"]}" data-doctype="Task" data-name="${data["name"]}" data-value="${data["name"]}">${data["name"]}:${data["subject"]}</a>`
			}
		
		if (data["bold"] ==1) {
			value=value.bold()
			console.log(value)
		}
		if (column["fieldname"] =="status")
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
		return value;
	},
	onload(report) {
		report.page.add_inner_button(__("Gantt chart"), () => {
			company=frappe.query_report.get_filter_value("company")
			project=frappe.query_report.get_filter_value("project")
			show_my_tasks=frappe.query_report.get_filter_value("show_my_tasks") 
			from_date=frappe.query_report.get_filter_value("from_date") 
			to_date=frappe.query_report.get_filter_value("to_date") 

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
	}
};
