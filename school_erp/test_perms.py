import frappe

def execute():
    frappe.init(site="edu.local")
    frappe.connect()
    try:
        # Check permission for Administrator
        frappe.set_user("Administrator")
        has_perm = frappe.has_permission("ID Card Generation Log", "read")
        print(f"Administrator has read perm: {has_perm}")
        
        # Check for another user
        frappe.set_user("vaishnavi@example.com")
        has_perm2 = frappe.has_permission("ID Card Generation Log", "read")
        print(f"Vaishnavi has read perm: {has_perm2}")
        
        # Test get_list
        frappe.set_user("Administrator")
        logs = frappe.get_list("ID Card Generation Log")
        print(f"Logs fetched: {len(logs)}")
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        frappe.destroy()

if __name__ == "__main__":
    execute()
