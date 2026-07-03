import frappe
import json

@frappe.whitelist()
def bulk_create_subject_groups(payload):
    frappe.only_for("System Manager")
    
    data = json.loads(payload)
    program = data.get("program")
    academic_year = data.get("academic_year")
    
    if not all([program, academic_year]):
        return {"status": "error", "message": "Program and Academic Year are required."}
        
    # Get all active batches (divisions) for this program
    batches = frappe.get_all("Student Group", filters={"program": program, "group_based_on": "Batch", "disabled": 0}, fields=["name", "student_group_name", "max_strength"])
    
    if not batches:
        return {"status": "error", "message": f"No active divisions found for program {program}."}
        
    # Get all courses (subjects) for this program
    program_doc = frappe.get_doc("Program", program)
    if not program_doc.courses:
        return {"status": "error", "message": f"No subjects (courses) mapped to program {program}."}
        
    created_count = 0
    
    for batch in batches:
        for course_row in program_doc.courses:
            course = course_row.course
            course_name = course_row.course_name or course
            
            # The naming convention will be: {Division Name} - {Subject}
            # Example: Std 8 - A - Mathematics
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
                doc = frappe.get_doc({
                    "doctype": "Student Group",
                    "student_group_name": group_name,
                    "group_based_on": "Course",
                    "program": program,
                    "course": course,
                    "academic_year": academic_year,
                    "max_strength": batch.max_strength
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
                
    return {"status": "success", "created": created_count}

@frappe.whitelist()
def get_student_groups_with_instructors():
    groups = frappe.get_all(
        "Student Group",
        fields=["name", "student_group_name", "academic_year", "academic_term", "group_based_on", "program", "batch", "course", "max_strength", "disabled", "room"],
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
        if i.parent not in instructor_map:
            instructor_map[i.parent] = []
        instructor_map[i.parent].append(i)
        
    for g in groups:
        g.instructors = instructor_map.get(g.name, [])
        
    return groups

def enroll_student_in_group(doc, method):
    """Automatically enroll the student in the Student Group for their Batch/Division upon Program Enrollment submission"""
    if doc.student_batch_name:
        # Check if a student group exists for this batch
        group_name = frappe.db.get_value("Student Group", {"student_group_name": doc.student_batch_name, "group_based_on": "Batch"}, "name")
        if group_name:
            group = frappe.get_doc("Student Group", group_name)
            # Check if student already in group
            existing = [s for s in group.students if s.student == doc.student]
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
                existing_cg = [s for s in cg_doc.students if s.student == doc.student]
                if not existing_cg:
                    cg_doc.append("students", {
                        "student": doc.student,
                        "student_name": doc.student_name,
                        "active": 1
                    })
                    cg_doc.save(ignore_permissions=True)

def unenroll_student_from_group(doc, method):
    """Automatically remove the student from the Student Group when Program Enrollment is cancelled"""
    if doc.student_batch_name:
        group_name = frappe.db.get_value("Student Group", {"student_group_name": doc.student_batch_name, "group_based_on": "Batch"}, "name")
        if group_name:
            group = frappe.get_doc("Student Group", group_name)
            initial_count = len(group.students)
            group.students = [s for s in group.students if s.student != doc.student]
            if len(group.students) != initial_count:
                group.save(ignore_permissions=True)

@frappe.whitelist()
def sync_existing_enrollments():
    enrollments = frappe.get_all('Program Enrollment', filters={'docstatus': 1}, fields=['name'])
    for e in enrollments:
        doc = frappe.get_doc('Program Enrollment', e.name)
        enroll_student_in_group(doc, None)
    frappe.db.commit()
    return f"Synced {len(enrollments)} enrollments"

def sync_draft_enrollments():
    enrollments = frappe.get_all('Program Enrollment', filters={'docstatus': 0}, fields=['name'])
    for e in enrollments:
        doc = frappe.get_doc('Program Enrollment', e.name)
        doc.submit()
    frappe.db.commit()
    return f"Submitted {len(enrollments)} enrollments"

def fix_instructor_permissions():
    frappe.permissions.add_permission('Student Group Instructor', 'Instructor', 0)
    frappe.db.commit()
    return "Permissions updated successfully!"

def add_role_to_sushant():
    user = frappe.get_doc('User', 'sushant@example.com')
    if not [r for r in user.roles if r.role == 'Instructor']:
        user.append('roles', {'role': 'Instructor'})
        user.save(ignore_permissions=True)
        frappe.db.commit()
    return "Role added to sushant@example.com!"

def sync_course_groups_with_batch():
    enrollments = frappe.get_all('Program Enrollment', filters={'docstatus': 1}, fields=['name'])
    for e in enrollments:
        doc = frappe.get_doc('Program Enrollment', e.name)
        enroll_student_in_group(doc, None)
    frappe.db.commit()
    return f"Synced {len(enrollments)} enrollments to course groups"

def fix_attendance_permissions():
    frappe.permissions.add_permission('Student Attendance', 'Instructor', 0)
    # The above adds read:1, write:0, create:0. Let's update it to allow create.
    perm_doc = frappe.get_doc('Custom DocPerm', {'parent': 'Student Attendance', 'role': 'Instructor'})
    perm_doc.read = 1
    perm_doc.write = 1
    perm_doc.create = 1
    perm_doc.submit = 1
    perm_doc.save(ignore_permissions=True)
    frappe.db.commit()
    return "Attendance Permissions updated successfully!"
