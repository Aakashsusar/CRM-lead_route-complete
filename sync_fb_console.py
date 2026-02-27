import frappe

def map_fields():
    print("Mapping fields for Ipshopy Seller Hub...")
    try:
        page = frappe.get_doc("Facebook Page", {"page_name": "Ipshopy Seller Hub"})
    except frappe.DoesNotExistError:
        print("Page 'Ipshopy Seller Hub' not found. Ensure forms were fetched.")
        return
        
    forms = frappe.get_all("Facebook Lead Form", filters={"page": page.id})
    print(f"Found {len(forms)} forms.")

    meta = frappe.get_meta("CRM Lead")
    fieldnames = [f.fieldname for f in meta.fields]
    if "custom_field_text" not in fieldnames:
        print("custom_field_text not found in CRM Lead, creating it...")
        custom_field = frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "CRM Lead",
            "fieldname": "custom_field_text",
            "label": "Custom Field Text",
            "fieldtype": "Small Text",
            "insert_after": "mobile_no"
        })
        custom_field.insert(ignore_permissions=True)
        frappe.db.commit()
        print("Created Custom Field.")

    for form_data in forms:
        form = frappe.get_doc("Facebook Lead Form", form_data.name)
        print(f"Form: {form.form_name}")
        for q in form.questions:
            label = q.label.lower()
            key = q.key.lower()
            
            mapped_field = "custom_field_text"
            
            if "name" in key: mapped_field = "first_name"
            if "email" in key: mapped_field = "email"
            if "phone" in key or "mobile" in key: mapped_field = "mobile_no"
            if "company" in key or "organization" in key: mapped_field = "organization"
                
            q.mapped_to_crm_field = mapped_field
            print(f"  Mapped {q.label} ({q.key}) -> {mapped_field}")
        
        form.save(ignore_permissions=True)
        print(f"Saved {form.form_name}")
        
    frappe.db.commit()
    print("Mapping complete.")

map_fields()
