import frappe

def run():
    user = "jak@gmail.com"
    frappe.set_user(user)

    try:
        leads = frappe.get_all("CRM Lead", filters={"current_department": "Google Ads"})
        if not leads:
            print("No leads in Google Ads.")
        else:
            lead_name = leads[0].name
            print(f"Testing route for lead: {lead_name}")
            from lead_routing.api.lead_transfer import mark_department_done
            res = mark_department_done(lead_name)
            print("Success:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()

