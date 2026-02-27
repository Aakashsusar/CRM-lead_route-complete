import frappe
from crm.api.create_sources import create_sources
frappe.reload_doc('lead_syncing', 'doctype', 'lead_sync_source')
create_sources()
