frappe.ui.form.on('Project', {
	refresh:function(frm){
	    if(!frm.doc.__islocal){
	        frm.add_custom_button(__("Add Tasks from Template"), () => {
	        frappe.db.get_list("Project Template", {pluck:'name'}).then((res) => {
        	    console.log(res)
        	        var d = new frappe.ui.Dialog({
        			title: __("Add Multiple Templates"),
        			fields: [
        				{
        					label: "Template",
        					fieldname: "template",
        					fieldtype: "MultiSelect",
        					options:res,
        					reqd:1
        					
        				}
        			],
        			primary_action: function () {
        				var data = d.get_values();
        				console.log(data)
        				
            				frappe.call({
            					method: "project_management.api.get_tasks_from_multiple_template",
            					args: {
            						template:data,
            						name:frm.doc.name
            					},
            					callback: function (r) {
            						if (!r.exc) {
            							if (r.message) {
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
        	})
	    

			}, __('Actions'));
	    }
	    
	}
})