import frappe

def validate_student_applicant(doc, method):
    # If transitioning to Fully Admitted, validate fees
    if doc.get("admission_sub_status") == "Fully Admitted":
        if "Education Manager" not in frappe.get_roles(frappe.session.user):
            student = frappe.db.get_value("Student", {"student_applicant": doc.name}, "name")
            if not student:
                frappe.throw("Cannot mark as Fully Admitted: No linked Student record found. Proceed through the normal admission steps first.")
            
            # Check if there's a submitted Fee that is paid (outstanding_amount = 0)
            paid_fee = frappe.db.exists("Fees", {"student": student, "outstanding_amount": ("<=", 0), "docstatus": 1})
            if not paid_fee:
                frappe.throw("Cannot mark as Fully Admitted: Fee is pending. Wait for fee payment or override via Education Manager.")

def on_update_student_applicant(doc, method):
    # Waitlist trigger
    if doc.has_value_changed("application_status") and doc.application_status == "Rejected":
        check_and_notify_waitlist(doc.program)
    elif doc.has_value_changed("admission_sub_status") and doc.admission_sub_status == "Not Admitted":
        check_and_notify_waitlist(doc.program)

def check_and_notify_waitlist(program):
    if not program:
        return
    
    # Find next ranked waitlisted applicant for this program
    next_waitlisted = frappe.get_all(
        "Student Applicant",
        filters={"program": program, "admission_sub_status": "Waitlisted"},
        order_by="creation asc",
        limit=1
    )
    
    if next_waitlisted:
        applicant = frappe.get_doc("Student Applicant", next_waitlisted[0].name)
        notify_guardian(applicant)

def notify_guardian(applicant):
    # Stub for SMS/WhatsApp notification dispatcher
    # TODO: Wire this to the actual Communication module or external SMS API
    frappe.logger().info(f"[Admissions] Seat opened for Waitlisted applicant {applicant.name} ({applicant.first_name}). Notification triggered to {applicant.student_mobile_number}.")
