frappe.views.calendar["Customer Holiday List"] ={
    field_map: {
		start: "holiday_date",
		end: "holiday_date",
		id: "name",
		title: "description",
		allDay: "allDay",
	},
	order_by: `from_date`,
	get_events_method: "project_management.project_management.doctype.customer_holiday_list.customer_holiday_list.get_events",
	filters: [
		{
			fieldtype: "Link",
			fieldname: "holiday_list",
			options: "Holiday List",
			label: __("Holiday List"),
		},
	],
}