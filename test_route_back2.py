import frappe

def run():
    frappe.set_user("Administrator")
    try:
        leads = frappe.get_all("CRM Lead", filters={"current_department": "Seller Onboarding"}, limit=1)
        if not leads:
            print("No leads in Seller Onboarding.")
            return

        lead_name = leads[0].name
        print(f"Testing route forward for lead: {lead_name}")
        
        from lead_routing.api.lead_transfer import mark_department_done, send_back_to_department
        res1 = mark_department_done(lead_name)
        print("Forward Success:", res1)

        print(f"Testing send_back for lead: {lead_name}")
        res2 = send_back_to_department(lead_name)
        print("Backward Success:", res2)
        
    except Exception as e:
        import traceback
        traceback.print_exc()

