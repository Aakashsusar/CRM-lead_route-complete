import frappe

def run():
    user = frappe.session.user
    user = "qwerty@gmail.com" # Account Manager User
    frappe.set_user(user)

    try:
        leads = frappe.get_all("CRM Lead", filters={"current_department": "Account Manager"})
        if not leads:
            print("No leads in Account Manager.")
        else:
            lead_name = leads[0].name
            print(f"Testing send_back for lead: {lead_name}")
            from lead_routing.api.lead_transfer import send_back_to_department
            res = send_back_to_department(lead_name)
            print("Success:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()

