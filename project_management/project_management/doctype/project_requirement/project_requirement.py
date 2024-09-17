# Copyright (c) 2024, FRAPPE TECHNOLOGIES PRIVATE LIMITED and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class ProjectRequirement(Document):
	pass


@frappe.whitelist()
def get_process_documents(process=None, module=None):
	filters = {}
	if process:
		filters['process'] = process
	if module:
		filters['module'] = module

	process_details = frappe.get_all(
		'Estimation Document', 
		fields=['document_name', 'process_name', 'configuration_effort', 'other_effort'], 
		filters=filters
	)

	return process_details



@frappe.whitelist()
def make_sales_order(source_name, target_doc=None, ignore_permissions=False):
	doclist = get_mapped_doc(
		"Project Requirement",
		source_name,
		{
			"Project Requirement": {
				"doctype": "Sales Order",
				"field_map": { 
				},
			},
		},
		target_doc,
		ignore_permissions=ignore_permissions,
	)

	return doclist


@frappe.whitelist()
def make_quotation(source_name, target_doc=None, ignore_permissions=False):
	doclist = get_mapped_doc(
		"Project Requirement",
		source_name,
		{
			"Project Requirement": {
				"doctype": "Quotation",
				"field_map": {
				},
			},
		},
		target_doc,
		ignore_permissions=ignore_permissions,
	)

	return doclist

@frappe.whitelist()
def make_project(source_name, target_doc=None, ignore_permissions=False):
	doclist = get_mapped_doc(
		"Project Requirement",
		source_name,
		{
			"Project Requirement": {
				"doctype": "Project",
				"field_map": {
				},
			},
		},
		target_doc,
		ignore_permissions=ignore_permissions,
	)

	return doclist