import frappe

def execute():
    dt = "ID Card Template"
    doc = frappe.get_doc("DocType", dt)
    
    new_fields = [
        {"fieldname": "cb_1", "fieldtype": "Column Break"},
        {"fieldname": "school_name", "fieldtype": "Data", "label": "School Name"},
        {"fieldname": "slogan", "fieldtype": "Data", "label": "Slogan"},
        {"fieldname": "school_logo", "fieldtype": "Attach Image", "label": "School Logo"},
        {"fieldname": "school_description", "fieldtype": "Small Text", "label": "School Description"},
        
        {"fieldname": "sb_1", "fieldtype": "Section Break", "label": "Field Toggles"},
        {"fieldname": "cb_2", "fieldtype": "Column Break"},
        {"fieldname": "show_student_name", "fieldtype": "Check", "label": "Show Student/Staff Name", "default": "1"},
        {"fieldname": "show_standard", "fieldtype": "Check", "label": "Show Standard", "default": "1"},
        {"fieldname": "show_photo", "fieldtype": "Check", "label": "Show Photo", "default": "1"},
        
        {"fieldname": "cb_3", "fieldtype": "Column Break"},
        {"fieldname": "show_mobile_no", "fieldtype": "Check", "label": "Show Mobile No"},
        {"fieldname": "show_address", "fieldtype": "Check", "label": "Show Address"},
        {"fieldname": "show_shift", "fieldtype": "Check", "label": "Show Shift"},
        
        {"fieldname": "sb_2", "fieldtype": "Section Break", "label": "Status"},
        {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Draft\nApproved", "default": "Draft"}
    ]
    
    # Check if they exist to prevent duplicates
    existing_fields = [f.fieldname for f in doc.fields]
    for field in new_fields:
        if field["fieldname"] not in existing_fields:
            doc.append("fields", field)
            
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    print("Added new configuration fields to ID Card Template.")
