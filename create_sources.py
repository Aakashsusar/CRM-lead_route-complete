import frappe

def create_sources():
    print("Creating Lead Sync Source records...")
    page = frappe.get_doc("Facebook Page", {"page_name": "Ipshopy Seller Hub"})
    forms = frappe.get_all("Facebook Lead Form", filters={"page": page.id})
    token = "Your Fb access token"

    for form in forms:
        if not frappe.db.exists("Lead Sync Source", {"facebook_lead_form": form.name}):
            doc = frappe.get_doc({
                "doctype": "Lead Sync Source",
                "type": "Facebook",
                "facebook_page": page.id,
                "facebook_lead_form": form.name,
                "access_token": token,
                "enabled": 1,
                "background_sync_frequency": "Every 2 Minutes"
            })
            # avoid calling fetch forms logic inside before_insert
            doc.insert(ignore_permissions=True)
            print(f"Created Sync Source for form: {form.name}")
        else:
            doc = frappe.get_doc("Lead Sync Source", {"facebook_lead_form": form.name})
            doc.background_sync_frequency = "Every 2 Minutes"
            doc.enabled = 1
            doc.access_token = token
            doc.save(ignore_permissions=True)
            print(f"Updated Sync Source for form: {form.name}")
            
    frappe.db.commit()
    print("Done configuring Sync Sources.")

create_sources()
