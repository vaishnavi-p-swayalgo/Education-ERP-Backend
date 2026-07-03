import frappe
def execute():
    doctypes_to_fix = ['ID Card Template', 'ID Card Generation Log', 'Library Book', 'Library Transaction', 'Transport Stop', 'Transport Route', 'Transport Vehicle', 'Transport Allocation', 'Transport Attendance']
    for dt in doctypes_to_fix:
        try:
            if frappe.db.exists('DocType', dt):
                frappe.db.set_value('DocType', dt, 'custom', 1)
                frappe.db.sql("delete from `tabDocPerm` where parent = %s", dt)
                doc = frappe.get_doc('DocType', dt)
                doc.append('permissions', {'role': 'System Manager', 'read': 1, 'write': 1, 'create': 1, 'delete': 1})
                doc.append('permissions', {'role': 'All', 'read': 1, 'write': 1, 'create': 1, 'delete': 1})
                doc.save(ignore_permissions=True)
                print('Fixed ' + dt)
        except Exception as e:
            print('Failed to fix ' + dt + ': ' + str(e))
    frappe.db.commit()
    print('Done')
