import frappe

def run():
    frappe.clear_cache()
    # Test as Account Manager user
    user = "qwerty@gmail.com"
    frappe.set_user(user)
    
    # Check if they can create CRM Lead
    can_create = frappe.has_permission("CRM Lead", ptype="create")
    print(f"Can {user} create CRM Lead? {can_create}")
    
    # Check list query for qwerty@gmail.com
    from lead_routing.api.permissions import get_permission_query
    query = get_permission_query()
    print(f"Permission query for {user}:\n{query}")

