# Copyright (c) 2024, FRAPPE TECHNOLOGIES PRIVATE LIMITED and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime
from frappe import _
class WorkingHourTemplate(Document):
	def validate(self):
		format = '%H:%M:%S' 
		time_diff=0
		for row in self.working_timeline:
			from_date=datetime.strptime(row.from_time, format)
			to_date=datetime.strptime(row.to_time, format)
			if from_date>=to_date:
				frappe.throw(_("From Time cannot be greater/equal than To Time"))
			time_diff=time_diff+((to_date-from_date).total_seconds())
		self.working_hours =time_diff