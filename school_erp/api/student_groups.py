import frappe
import json

@frappe.whitelist()
def bulk_create_subject_groups(payload):
    """
    Bulk creates Course-based Student Groups from Batch divisions.
    Expected payload (JSON string): {"program": "...", "academic_year": "..."}
    """
    frappe.only_for("System Manager")
    
    try:
        data = json.loads(payload)
    except Exception:
        frappe.throw("Invalid JSON payload provided.")

    program = data.get("program")
    academic_year = data.get("academic_year")
    
    if not all([program, academic_year]):
        frappe.throw("Program and Academic Year are required.")
        
    # Get all active batches (divisions) for this program
    batches = frappe.get_all(
        "Student Group", 
        filters={"program": program, "group_based_on": "Batch", "disabled": 0}, 
        fields=["name", "student_group_name", "max_strength"]
    )
    
    if not batches:
        frappe.throw(f"No active divisions found for program {program}.")
        
    # Get all courses (subjects) for this program
    try:
        program_doc = frappe.get_doc("Program", program)
    except frappe.DoesNotExistError:
        frappe.throw(f"Program {program} does not exist.")
        
    if not program_doc.courses:
        frappe.throw(f"No subjects (courses) mapped to program {program}.")
        
    created_count = 0
    
    for batch in batches:
        for course_row in program_doc.courses:
            course = course_row.course
            course_name = course_row.course_name or course
            
            # The naming convention will be: {Division Name} - {Subject}
            group_name = f"{batch.student_group_name} - {course_name}"
            
            # Check if this course-level group already exists
            exists = frappe.db.exists("Student Group", {
                "program": program,
                "course": course,
                "group_based_on": "Course",
                "academic_year": academic_year,
                "student_group_name": group_name
            })
            
            if not exists:
                try:
                    doc = frappe.get_doc({
                        "doctype": "Student Group",
                        "student_group_name": group_name,
                        "group_based_on": "Course",
                        "program": program,
                        "course": course,
                        "academic_year": academic_year,
                        "max_strength": batch.max_strength,
                        "batch": batch.name
                    })
                    
                    # Add students from the batch group
                    batch_doc = frappe.get_doc("Student Group", batch.name)
                    for s in batch_doc.students:
                        doc.append("students", {
                            "student": s.student,
                            "student_name": s.student_name,
                            "active": 1
                        })
                        
                    doc.insert(ignore_permissions=True)
                    created_count += 1
                except Exception as e:
                    frappe.log_error(message=frappe.get_traceback(), title=f"Failed to create Student Group {group_name}")
                    # Continue creating others even if one fails
                    continue
                
    return {"status": "success", "created": created_count}

@frappe.whitelist()
def get_student_groups_with_instructors():
    """
    Fetches student groups along with their assigned instructors.
    """
    try:
        groups = frappe.get_all(
            "Student Group",
            fields=[
                "name", "student_group_name", "academic_year", "academic_term", 
                "group_based_on", "program", "batch", "course", "max_strength", 
                "disabled", "room"
            ],
            order_by="academic_year desc",
            limit_page_length=500
        )
        
        # Fetch instructors for all groups
        instructors = frappe.get_all(
            "Student Group Instructor",
            fields=["parent", "instructor", "instructor_name"],
            filters={"parenttype": "Student Group"}
        )
        
        instructor_map = {}
        for i in instructors:
            instructor_map.setdefault(i.parent, []).append(i)
            
        for g in groups:
            g.instructors = instructor_map.get(g.name, [])
            
        return groups
    except Exception as e:
        frappe.log_error(title="Failed to fetch student groups with instructors", message=frappe.get_traceback())
        frappe.throw("An error occurred while fetching student groups.")

def enroll_student_in_group(doc, method):
    """
    Automatically enroll the student in the Student Group for their Batch/Division 
    upon Program Enrollment submission. (Hooked via doc_events)
    """
    if doc.student_batch_name:
        group_name = frappe.db.get_value("Student Group", {
            "student_group_name": doc.student_batch_name, 
            "group_based_on": "Batch"
        }, "name")
        
        if group_name:
            try:
                group = frappe.get_doc("Student Group", group_name)
                existing = any(s.student == doc.student for s in group.students)
                
                if not existing:
                    group.append("students", {
                        "student": doc.student,
                        "student_name": doc.student_name,
                        "active": 1
                    })
                    group.save(ignore_permissions=True)
                    
                # Also enroll in all Course groups generated for this batch
                course_groups = frappe.get_all("Student Group", filters={
                    "group_based_on": "Course",
                    "student_group_name": ["like", f"{doc.student_batch_name} - %"]
                })
                
                for cg in course_groups:
                    cg_doc = frappe.get_doc("Student Group", cg.name)
                    existing_cg = any(s.student == doc.student for s in cg_doc.students)
                    if not existing_cg:
                        cg_doc.append("students", {
                            "student": doc.student,
                            "student_name": doc.student_name,
                            "active": 1
                        })
                        cg_doc.save(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(title=f"Failed auto-enrollment for {doc.student}", message=frappe.get_traceback())
                # Do not throw to prevent blocking the Program Enrollment submission
                
def unenroll_student_from_group(doc, method):
    """
    Automatically remove the student from the Student Group when 
    Program Enrollment is cancelled. (Hooked via doc_events)
    """
    if doc.student_batch_name:
        group_name = frappe.db.get_value("Student Group", {
            "student_group_name": doc.student_batch_name, 
            "group_based_on": "Batch"
        }, "name")
        
        if group_name:
            try:
                group = frappe.get_doc("Student Group", group_name)
                initial_count = len(group.students)
                
                # Filter out the cancelled student
                group.students = [s for s in group.students if s.student != doc.student]
                
                if len(group.students) != initial_count:
                    group.save(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(title=f"Failed auto-unenrollment for {doc.student}", message=frappe.get_traceback())
