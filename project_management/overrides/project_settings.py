import frappe
from frappe import _
from datetime import datetime
def validate(self,method):
    format = '%H:%M:%S' 
    if self.custom_duration and int(self.custom_duration) > 86400:
        frappe.throw(_("Duration cannot be greater than 24 hours"))
    if self.custom_from_time and self.custom_to_time_:
        from_date=datetime.strptime(self.custom_from_time, format)
        to_date=datetime.strptime(self.custom_to_time_, format)
        if from_date>=to_date:
            frappe.throw(_("From Time cannot be greater/equal than To Time"))
        else:
            time_diff=to_date-from_date
            seconds_diff = time_diff.total_seconds()
            self.custom_duration=seconds_diff