frappe.ui.form.on('Project', {
	refresh:function(frm){
	    if(!frm.doc.__islocal){
	        frm.add_custom_button(__("Add Tasks from Template"), () => {
				var fields = [
					{
						fieldtype: "Data",
						fieldname: "name",
						read_only: 1,
						hidden: 1,
					},
					{
						fieldname: "subject",
						fieldtype: "Data",
						in_list_view: 1,
						read_only: 1,
						label: "Subject"
					   },
					{
						fieldtype: "Link",
						fieldname: "task",
						read_only: 1,
						in_list_view: 1,
						label: __("Template Task"),
						options: "Task",
					},
					{
						
							default: "0",
							fieldname: "expected_time",
							fieldtype: "Float",
							label: "Expected Time (in hours)",
							oldfieldname: "expected_time",
							in_list_view: 1,
							read_only: 1,

						   	
					},
					{
						
							fieldname: "type",
							fieldtype: "Link",
							label: "Task Type",
							options: "Task Type",
							in_list_view: 1,
							read_only: 1,
						   
					},

					
					{
						fieldtype: "Date",
						fieldname: "start_date",
						label: __("Start Date"),
						reqd:1,
						in_list_view: 1,
						change: () => {
							
							var template=d.get_value("template");
							var as_per=d.get_value("as_per");
							var task_table=d.get_value("task_table");
							frappe.call({
								method: "project_management.api.get_task_value",
								args: {
									template:template,
									project:frm.doc.name,
									company:frm.doc.company,
									as_per:as_per,
									custom_start_dates:task_table
								},
								callback: function (r) {
									if (!r.exc) {
										
										if (r.message) {
											d.fields_dict.task_table.df.data =r.message

											d.fields_dict.task_table.refresh()
											d.fields_dict.task_table.grid.reset_grid()
										}
									}
								},
							})
						}
						
					},
					{
						fieldtype: "Date",
						fieldname: "end_date",
						in_list_view: 1,
						label: __("End Date"),
						read_only: 1,

					},
				]
				var data=[];
        	        var d = new frappe.ui.Dialog({
        			title: __("Add Multiple Templates"),
        			fields: [
        				{
        					label: "Template",
        					fieldname: "template",
        					fieldtype: "Link",
        					options:"Project Template",
        					reqd:1,
							change: () => {
								d.fields_dict.template.$input.blur()
								
								var template=d.get_value("template");
								var as_per=d.get_value("as_per");
								frappe.call({
									method: "project_management.api.get_task_value",
									args: {
										template:template,
										project:frm.doc.name,
										company:frm.doc.company,
										as_per:as_per
									},
									callback: function (r) {
										if (!r.exc) {
											
											if (r.message) {
												d.fields_dict.task_table.df.data =r.message

												d.fields_dict.task_table.refresh()
												
											}
										}
									},
								})

							}
        					
        				},
						{
        					label: "Parent Task",
        					fieldname: "parent_task",
        					fieldtype: "Link",
        					options:"Task",
        					depends_on: "eval:doc.template",
							get_query: function () {
									return{
										filters:{
										project:frm.doc.name,
										is_group:1
										}
									
									}
								
							}
							
        					
        				},
						{
							label: "As Per Task Template",
        					fieldname: "as_per",
        					fieldtype: "Check",
							description:"The start and end date will be As Per Task Template's duration and start",
        					default:1,
							change: () => {
								d.fields_dict.template.$input.blur()
								
								var template=d.get_value("template");
								var as_per=d.get_value("as_per");
								frappe.call({
									method: "project_management.api.get_task_value",
									args: {
										template:template,
										project:frm.doc.name,
										company:frm.doc.company,
										as_per:as_per
									},
									callback: function (r) {
										if (!r.exc) {
											
											if (r.message) {
												d.fields_dict.task_table.df.data =r.message

												d.fields_dict.task_table.refresh()
											}
										}
									},
								})

							}


						},
						{
							fieldname: "task_table",
							fieldtype: "Table",
							label: "Tasks Update Values",
							cannot_add_rows: true,
							cannot_delete_rows: true,
							in_place_edit: true,
							depends_on: "eval:doc.template",
							fields: fields,
							reqd:1,
						

						},
        			],
        			primary_action: function () {
        				var data = d.get_values();
            				frappe.call({
            					method: "project_management.api.get_tasks_from_multiple_template",
            					args: {
            						template:data.template,
									parent_task:data.parent_task,
            						name:frm.doc.name,
									tasks:data.task_table
									
									
            					},
            					callback: function (r) {
            						if (!r.exc) {
            							if (r.message) {
											frm.reload_doc();
            							    frappe.msgprint("Tasks Assigned to Project")
            							}
            							d.hide();
            						}
            					},
            				
        				})
        				
        			},
        			primary_action_label: __("Import"),
        		});
				//d.get_field("task_table").grid.only_sortable();
				
        		d.show();
				
	    

			}, __('Actions'));
	    }
	    
	}
})