import frappe
import traceback

def execute():
    frappe.flags.in_import = True
    
    doctypes = [
        {
            "doctype": "DocType", "module": "School ERP", "custom": 0, "name": "ID Card Template", "naming_rule": "By fieldname", "autoname": "field:template_name",
            "fields": [
                {"fieldname": "template_name", "fieldtype": "Data", "label": "Template Name", "reqd": 1},
                {"fieldname": "target_role", "fieldtype": "Select", "label": "Target Role", "options": "Student\nStaff", "reqd": 1},
                {"fieldname": "background_image", "fieldtype": "Attach Image", "label": "Background Image"},
                {"fieldname": "layout_json", "fieldtype": "Code", "label": "Layout JSON", "options": "JSON"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1}]
        },
        {
            "doctype": "DocType", "module": "School ERP", "custom": 0, "name": "ID Card Generation Log", "naming_rule": "Expression", "autoname": "format:IDC-LOG-{YYYY}-{MM}-{#####}",
            "fields": [
                {"fieldname": "template", "fieldtype": "Link", "label": "Template", "options": "ID Card Template", "reqd": 1},
                {"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year", "options": "Academic Year"},
                {"fieldname": "program", "fieldtype": "Link", "label": "Standard / Program", "options": "Program"},
                {"fieldname": "student_group", "fieldtype": "Link", "label": "Division / Student Group", "options": "Student Group"},
                {"fieldname": "generated_count", "fieldtype": "Int", "label": "Generated Count"},
                {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Pending\nCompleted\nFailed"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1}]
        },
        {
            "doctype": "DocType", "module": "School ERP", "custom": 0, "name": "Library Book", "naming_rule": "By fieldname", "autoname": "field:title",
            "fields": [
                {"fieldname": "title", "fieldtype": "Data", "label": "Title", "reqd": 1},
                {"fieldname": "author", "fieldtype": "Data", "label": "Author"},
                {"fieldname": "isbn", "fieldtype": "Data", "label": "ISBN"},
                {"fieldname": "rack_location", "fieldtype": "Data", "label": "Rack Location"},
                {"fieldname": "total_copies", "fieldtype": "Int", "label": "Total Copies", "default": "1"},
                {"fieldname": "available_copies", "fieldtype": "Int", "label": "Available Copies", "default": "1"},
                {"fieldname": "is_periodical", "fieldtype": "Check", "label": "Is Periodical"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1}]
        },
        {
            "doctype": "DocType", "module": "School ERP", "custom": 0, "name": "Library Transaction", "naming_rule": "Expression", "autoname": "format:LIB-TXN-{YYYY}-{#####}",
            "fields": [
                {"fieldname": "book", "fieldtype": "Link", "label": "Book", "options": "Library Book", "reqd": 1},
                {"fieldname": "issued_to", "fieldtype": "Link", "label": "Issued To (Student)", "options": "Student"},
                {"fieldname": "staff_member", "fieldtype": "Link", "label": "Issued To (Staff)", "options": "Employee"},
                {"fieldname": "issue_date", "fieldtype": "Date", "label": "Issue Date", "reqd": 1},
                {"fieldname": "due_date", "fieldtype": "Date", "label": "Due Date"},
                {"fieldname": "return_date", "fieldtype": "Date", "label": "Return Date"},
                {"fieldname": "fine_amount", "fieldtype": "Currency", "label": "Fine Amount", "default": "0"},
                {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Issued\nReturned\nOverdue"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1}]
        },
        {
            "doctype": "DocType", "module": "School ERP", "custom": 0, "istable": 1, "name": "Transport Stop",
            "fields": [
                {"fieldname": "stop_name", "fieldtype": "Data", "label": "Stop Name", "in_list_view": 1},
                {"fieldname": "pickup_time", "fieldtype": "Time", "label": "Pickup Time", "in_list_view": 1},
                {"fieldname": "drop_time", "fieldtype": "Time", "label": "Drop Time", "in_list_view": 1},
                {"fieldname": "distance_from_school", "fieldtype": "Float", "label": "Distance (km)"}
            ]
        },
        {
            "doctype": "DocType", "module": "School ERP", "custom": 0, "name": "Transport Route", "naming_rule": "By fieldname", "autoname": "field:route_name",
            "fields": [
                {"fieldname": "route_name", "fieldtype": "Data", "label": "Route Name", "reqd": 1},
                {"fieldname": "stops", "fieldtype": "Table", "label": "Stops", "options": "Transport Stop"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1}]
        },
        {
            "doctype": "DocType", "module": "School ERP", "custom": 0, "name": "Transport Vehicle", "naming_rule": "By fieldname", "autoname": "field:vehicle_number",
            "fields": [
                {"fieldname": "vehicle_number", "fieldtype": "Data", "label": "Vehicle Number (Registration)", "reqd": 1},
                {"fieldname": "capacity", "fieldtype": "Int", "label": "Capacity (Seats)", "reqd": 1},
                {"fieldname": "route", "fieldtype": "Link", "label": "Assigned Route", "options": "Transport Route"},
                {"fieldname": "driver", "fieldtype": "Link", "label": "Driver", "options": "Employee"},
                {"fieldname": "attendant", "fieldtype": "Link", "label": "Attendant", "options": "Employee"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1}]
        },
        {
            "doctype": "DocType", "module": "School ERP", "custom": 0, "name": "Transport Allocation", "naming_rule": "Expression", "autoname": "format:TR-ALC-{YYYY}-{#####}",
            "fields": [
                {"fieldname": "student", "fieldtype": "Link", "label": "Student", "options": "Student", "reqd": 1},
                {"fieldname": "route", "fieldtype": "Link", "label": "Route", "options": "Transport Route", "reqd": 1},
                {"fieldname": "vehicle", "fieldtype": "Link", "label": "Vehicle", "options": "Transport Vehicle"},
                {"fieldname": "pickup_stop", "fieldtype": "Data", "label": "Pickup Stop Name"},
                {"fieldname": "drop_stop", "fieldtype": "Data", "label": "Drop Stop Name"},
                {"fieldname": "fee_amount", "fieldtype": "Currency", "label": "Transport Fee Amount"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1}]
        },
        {
            "doctype": "DocType", "module": "School ERP", "custom": 0, "name": "Transport Attendance", "naming_rule": "Expression", "autoname": "format:TR-ATT-{YYYY}-{MM}-{DD}-{vehicle}",
            "fields": [
                {"fieldname": "date", "fieldtype": "Date", "label": "Date", "reqd": 1},
                {"fieldname": "vehicle", "fieldtype": "Link", "label": "Vehicle", "options": "Transport Vehicle", "reqd": 1},
                {"fieldname": "trip_type", "fieldtype": "Select", "label": "Trip Type", "options": "Pickup\nDrop"},
                {"fieldname": "students_present", "fieldtype": "Int", "label": "Students Present"},
                {"fieldname": "log_details", "fieldtype": "Code", "label": "Attendance Log JSON", "options": "JSON"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1}]
        }
    ]

    for d in doctypes:
        try:
            if not frappe.db.exists('DocType', d['name']):
                doc = frappe.get_doc(d)
                doc.insert(ignore_permissions=True)
                print(f"Successfully created: {d['name']}")
            else:
                print(f"Already exists: {d['name']}")
        except ImportError:
            # Frappe generates the file but fails to import it in the same process sometimes. We commit the DB changes.
            frappe.db.commit()
            print(f"Created (caught ImportError): {d['name']}")
        except Exception as e:
            print(f"Error creating {d['name']}: {e}")
            traceback.print_exc()

    frappe.db.commit()
    print("All backend Doctypes processed successfully.")

