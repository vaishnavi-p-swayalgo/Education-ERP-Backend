import frappe

def execute():
    frappe.init(site="edu.local")
    frappe.connect()
    try:
        doctype = 'ID Card Generation Log'
        # Remove existing custom perms for this doctype to avoid conflicts
        frappe.db.delete("Custom DocPerm", {"parent": doctype})
        
        # Add for 'All'
        doc = frappe.new_doc("Custom DocPerm")
        doc.parent = doctype
        doc.parenttype = "DocType"
        doc.parentfield = "permissions"
        doc.role = "All"
        doc.read = 1
        doc.write = 1
        doc.create = 1
        doc.submit = 1
        doc.cancel = 1
        doc.delete = 1
        doc.insert()
        
        # Add for 'System Manager' just in case
        doc2 = frappe.new_doc("Custom DocPerm")
        doc2.parent = doctype
        doc2.parenttype = "DocType"
        doc2.parentfield = "permissions"
        doc2.role = "System Manager"
        doc2.read = 1
        doc2.write = 1
        doc2.create = 1
        doc2.submit = 1
        doc2.cancel = 1
        doc2.delete = 1
        doc2.insert()
        
        frappe.db.commit()
        frappe.clear_cache(doctype=doctype)
        print("Permissions added successfully for All.")
    finally:
        frappe.destroy()

if __name__ == "__main__":
    execute()
