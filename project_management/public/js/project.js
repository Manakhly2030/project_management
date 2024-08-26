frappe.ui.form.on('Project', {
	refresh:function(frm){
	    if(!frm.doc.__islocal){
	        frm.add_custom_button(__("Add Tasks from Template"), () => {
	       
        	        var d = new frappe.ui.Dialog({
        			title: __("Add Multiple Templates"),
        			fields: [
        				{
        					label: "Template",
        					fieldname: "template",
        					fieldtype: "Link",
        					options:"Project Template",
        					reqd:1
        					
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
							
        					
        				}
        			],
        			primary_action: function () {
        				var data = d.get_values();
            				frappe.call({
            					method: "project_management.api.get_tasks_from_multiple_template",
            					args: {
            						template:data.template,
									parent_task:data.parent_task,
            						name:frm.doc.name
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