import frappe

def run():
    roles_to_update = [
        "Google Ads User",
        "Product Listing User",
        "Completion User",
        "Account Manager User",
        "Seller Onboarding User"
    ]
    
    for role in roles_to_update:
        perms = frappe.get_all("Custom DocPerm", filters={"parent": "CRM Lead", "role": role})
        if perms:
            for p in perms:
                frappe.db.set_value("Custom DocPerm", p.name, "create", 1)
        
        # Also check standard DocPerm
        std_perms = frappe.get_all("DocPerm", filters={"parent": "CRM Lead", "role": role})
        if std_perms:
            for p in std_perms:
                frappe.db.set_value("DocPerm", p.name, "create", 1)
                
    frappe.db.commit()
    print("Permissions updated.")

