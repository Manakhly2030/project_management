import frappe
from frappe import _
from datetime import datetime
def validate(self,method):
    format = '%H:%M:%S' 
    time_diff=0
    for row in self.custom_working_timeline_:
        from_date=datetime.strptime(row.from_time, format)
        to_date=datetime.strptime(row.to_time, format)
        if from_date>=to_date:
            frappe.throw(_("From Time cannot be greater/equal than To Time"))
        time_diff=time_diff+((to_date-from_date).total_seconds())
    self.custom_working_hours =time_diff
    