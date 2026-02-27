import frappe

def run():
    try:
        from crm.api.hierarchy import _original_get_hierarchy_tree
        
        user = "abc@gmail.com" # Product Listing user
        user_roles = frappe.get_roles(user)
        print(f"User: {user} | Roles: {user_roles}")

        dept_stages = frappe.get_all(
            "Department Pipeline Stage",
            filters={"enabled": 1},
            fields=["name", "stage_name", "department_role", "manager_role"],
        )

        user_dept_names = set()
        for stage in dept_stages:
            if (stage.department_role and stage.department_role in user_roles) or \
               (stage.manager_role and stage.manager_role in user_roles):
                user_dept_names.add(stage.name)

        print(f"Matched Department Pipeline Stages: {user_dept_names}")

        if not user_dept_names:
            print("No department matching found. Original tree would be returned.")
            return

        full_tree = _original_get_hierarchy_tree()

        filtered_tree = []
        for shift in full_tree:
            filtered_shift = dict(shift)
            filtered_depts = []

            for dept in shift.get("departments", []):
                dept_name = dept.get("name", "")
                dept_display = dept.get("department_name", "")

                should_include = False
                for ud in user_dept_names:
                    stage_doc = frappe.get_doc("Department Pipeline Stage", ud)
                    if (stage_doc.stage_name == dept_display or stage_doc.name == dept_name):
                        should_include = True
                        break
                
                if should_include:
                    filtered_depts.append(dept)

            if filtered_depts:
                filtered_shift["departments"] = filtered_depts
                filtered_tree.append(filtered_shift)

        print(f"\nFiltered Tree length: {len(filtered_tree)}")
        for shift in filtered_tree:
            print(f"Shift: {shift.get('shift_name')}")
            for dept in shift.get("departments", []):
                print(f"  - Dept: {dept.get('department_name')}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

