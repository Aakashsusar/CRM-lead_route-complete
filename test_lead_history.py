import frappe

def run():
    frappe.set_user("abc@gmail.com")
    try:
        from lead_routing.api.lead_history import get_my_lead_history
        history = get_my_lead_history()
        print(f"User: {history.get('user')}")
        print(f"Currently assigned leads: {len(history.get('currently_assigned', []))}")
        print(f"Completed leads: {len(history.get('completed', []))}")
        print("Completed Leads List:")
        for l in history.get('completed', []):
            print(f"- {l.get('name')}")
    except Exception as e:
        import traceback
        traceback.print_exc()

