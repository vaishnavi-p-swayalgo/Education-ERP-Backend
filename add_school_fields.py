import frappe
from frappe import _

def add_custom_fields():
    fields = [
        # --- School Identity ---
        {
            "dt": "Company",
            "fieldname": "school_section",
            "label": "School Information",
            "fieldtype": "Section Break",
            "insert_after": "domain",
        },
        {
            "dt": "Company",
            "fieldname": "school_type",
            "label": "School Type",
            "fieldtype": "Select",
            "options": "\nPrimary\nSecondary\nHigher Secondary\nUniversity\nCoaching\nVocational",
            "insert_after": "school_section",
        },
        {
            "dt": "Company",
            "fieldname": "school_category",
            "label": "School Category",
            "fieldtype": "Select",
            "options": "\nGovernment\nPrivate\nAided\nInternational",
            "insert_after": "school_type",
        },
        {
            "dt": "Company",
            "fieldname": "affiliation_board",
            "label": "Affiliation Board",
            "fieldtype": "Select",
            "options": "\nCBSE\nICSE\nState Board\nIB\nIGCSE\nCambridge",
            "insert_after": "school_category",
        },
        {
            "dt": "Company",
            "fieldname": "affiliation_number",
            "label": "Affiliation Number",
            "fieldtype": "Data",
            "insert_after": "affiliation_board",
        },
        {
            "dt": "Company",
            "fieldname": "udise_code",
            "label": "UDISE Code",
            "fieldtype": "Data",
            "insert_after": "affiliation_number",
        },
        {
            "dt": "Company",
            "fieldname": "registration_number",
            "label": "Govt Registration Number",
            "fieldtype": "Data",
            "insert_after": "udise_code",
        },
        {
            "dt": "Company",
            "fieldname": "year_of_establishment",
            "label": "Year of Establishment",
            "fieldtype": "Int",
            "insert_after": "registration_number",
        },

        # --- Academic Setup ---
        {
            "dt": "Company",
            "fieldname": "academic_section",
            "label": "Academic Configuration",
            "fieldtype": "Section Break",
            "insert_after": "year_of_establishment",
        },
        {
            "dt": "Company",
            "fieldname": "medium_of_instruction",
            "label": "Medium of Instruction",
            "fieldtype": "Select",
            "options": "\nEnglish\nHindi\nRegional\nBilingual",
            "insert_after": "academic_section",
        },
        {
            "dt": "Company",
            "fieldname": "classes_offered",
            "label": "Classes Offered",
            "fieldtype": "Small Text",
            "insert_after": "medium_of_instruction",
        },
        {
            "dt": "Company",
            "fieldname": "streams_offered",
            "label": "Streams Offered",
            "fieldtype": "Select",
            "options": "\nScience\nCommerce\nArts\nVocational\nAll",
            "insert_after": "classes_offered",
        },
        {
            "dt": "Company",
            "fieldname": "shift_type",
            "label": "Shift Type",
            "fieldtype": "Select",
            "options": "\nMorning\nAfternoon\nBoth",
            "insert_after": "streams_offered",
        },
        {
            "dt": "Company",
            "fieldname": "academic_calendar_type",
            "label": "Academic Calendar Type",
            "fieldtype": "Select",
            "options": "\nApril-March\nJune-May\nJanuary-December",
            "insert_after": "shift_type",
        },

        # --- Principal Info ---
        {
            "dt": "Company",
            "fieldname": "principal_section",
            "label": "Principal Information",
            "fieldtype": "Section Break",
            "insert_after": "academic_calendar_type",
        },
        {
            "dt": "Company",
            "fieldname": "principal_name",
            "label": "Principal Name",
            "fieldtype": "Data",
            "insert_after": "principal_section",
        },
        {
            "dt": "Company",
            "fieldname": "principal_email",
            "label": "Principal Email",
            "fieldtype": "Data",
            "options": "Email",
            "insert_after": "principal_name",
        },
        {
            "dt": "Company",
            "fieldname": "principal_phone",
            "label": "Principal Phone",
            "fieldtype": "Data",
            "insert_after": "principal_email",
        },

        # --- App Config ---
        {
            "dt": "Company",
            "fieldname": "app_config_section",
            "label": "App Configuration",
            "fieldtype": "Section Break",
            "insert_after": "principal_phone",
        },
        {
            "dt": "Company",
            "fieldname": "school_slug",
            "label": "School Slug",
            "fieldtype": "Data",
            "insert_after": "app_config_section",
        },
        {
            "dt": "Company",
            "fieldname": "school_status",
            "label": "School Status",
            "fieldtype": "Select",
            "options": "\nPending Approval\nActive\nSuspended",
            "default": "Pending Approval",
            "insert_after": "school_slug",
        },
        {
            "dt": "Company",
            "fieldname": "onboarding_completed",
            "label": "Onboarding Completed",
            "fieldtype": "Check",
            "default": "0",
            "insert_after": "school_status",
        },
    ]

    for f in fields:
        if frappe.db.exists("Custom Field", {"dt": f["dt"], "fieldname": f["fieldname"]}):
            print(f"SKIP (exists): {f['fieldname']}")
            continue
        doc = frappe.get_doc({"doctype": "Custom Field", **f})
        doc.insert()
        print(f"ADDED: {f['fieldname']}")

    frappe.db.commit()
    print("\n✅ All school fields added successfully.")

add_custom_fields()
