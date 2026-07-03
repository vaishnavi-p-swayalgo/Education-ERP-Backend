import frappe

def execute():
    frappe.init(site="edu.local")
    frappe.connect()
    try:
        doctype = 'ID Card Generation Log'
        if not frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": "System Manager"}):
            doc = frappe.new_doc("Custom DocPerm")
            doc.parent = doctype
            doc.parenttype = "DocType"
            doc.parentfield = "permissions"
            doc.role = "System Manager"
            doc.read = 1
            doc.write = 1
            doc.create = 1
            doc.submit = 1
            doc.cancel = 1
            doc.delete = 1
            doc.insert()
            frappe.db.commit()
            print("Permissions added successfully.")
        else:
            print("Permissions already exist.")
    finally:
        frappe.destroy()

if __name__ == "__main__":
    execute()
