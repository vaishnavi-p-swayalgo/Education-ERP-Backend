import frappe

def execute():
    # Update module of Doctypes
    doctypes = ["Admission Inquiry", "Admission Document Checklist", "RTE Reimbursement Record"]
    for dt_name in doctypes:
        doc = frappe.get_doc("DocType", dt_name)
        doc.module = "School ERP"
        doc.save()
        print(f"Moved {dt_name} to School ERP module")

    frappe.db.commit()
