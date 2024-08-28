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
						fieldtype: "Date",
						fieldname: "start_date",
						label: __("Start Date"),
						in_list_view: 1,
						default: frappe.datetime.nowdate(),
					},
					{
						fieldtype: "Date",
						fieldname: "end_date",
						in_list_view: 1,
						label: __("End Date"),
						read_only: 1,
						// onchange: function () {
						// 	debugger
						// 	var task_table_data =d.get_value("task_table");
						// 	if (task_table_data.length > 0) {
						// 		var frist_row_endate=task_table_data[0].end_date
						// 		 frist_row_endate = new Date(frist_row_endate);
						// 	for (let index = 1; index < task_table_data.length; index++) {
						// 		var start_date=task_table_data[index].start_date
						// 		start_date = new Date(start_date);
						// 		if(start_date <= frist_row_endate){
						// 			frappe.call({
						// 				method: "project_management.api.next_woking_date",
						// 				args: {
						// 					date: `${start_date.getFullYear()}-${String(start_date.getMonth()).padStart(2, '0')}-${String(start_date.getDate()).padStart(2, '0')}`,
						// 					company:frm.doc.company
						// 				},
						// 				callback: function (r) {
						// 					if (!r.exc) {
												
						// 						if (r.message) {
						// 							d.fields_dict.task_table.df.data[index].start_date =r.message
	
						// 							d.fields_dict.task_table.refresh()
						// 						}
						// 					}
						// 				},
						// 			})

									
						// 		}
						// 		frist_row_endate = new Date(task_table_data[index].end_date);
								
								
						// 	}
								
						// 	}
							

						// },
						// default: frappe.datetime.nowdate(),

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
								debugger
								var template=d.get_value("template");
								frappe.call({
									method: "project_management.api.get_task_value",
									args: {
										template:template,
										project:frm.doc.name,
										company:frm.doc.company
									},
									callback: function (r) {
										// debugger
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
							fieldname: "task_table",
							fieldtype: "Table",
							label: "Tasks Update Values",
							 cannot_add_rows: true,
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
        		d.show();
        
	    

			}, __('Actions'));
	    }
	    
	}
})