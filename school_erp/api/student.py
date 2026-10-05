import frappe
from frappe import _

@frappe.whitelist()
def get_student_courses(student_name):
    """
    Fetch all courses assigned to a student via Student Group mappings OR Program Enrollments.
    """
    if not student_name:
        frappe.throw(_("Student Name is required"))
        
    courses_sg = frappe.db.sql("""
        SELECT 
            c.name as course,
            c.course_name,
            c.department,
            c.description,
            c.hero_image,
            c.subject_type,
            sg.name as student_group
        FROM `tabStudent Group Student` sgs
        JOIN `tabStudent Group` sg ON sgs.parent = sg.name
        JOIN `tabCourse` c ON sg.course = c.name
        WHERE sgs.student = %s 
          AND sg.group_based_on = 'Course'
    """, (student_name,), as_dict=True)
    
    courses_pe = frappe.db.sql("""
        SELECT 
            c.name as course,
            c.course_name,
            c.department,
            c.description,
            c.hero_image,
            c.subject_type,
            'Program Enrollment' as student_group
        FROM `tabProgram Enrollment` pe
        JOIN `tabProgram Course` pc ON pc.parent = pe.program
        JOIN `tabCourse` c ON pc.course = c.name
        WHERE pe.student = %s
          AND pe.docstatus < 2
    """, (student_name,), as_dict=True)
    
    all_courses = {}
    for c in courses_pe:
        all_courses[c.course] = c
    for c in courses_sg:
        all_courses[c.course] = c
        
    return list(all_courses.values())

@frappe.whitelist()
def get_student_timetable(student_name, date_start=None, date_end=None):
    """
    Fetch the course schedule for a student based on their group assignments.
    """
    if not student_name:
        frappe.throw(_("Student Name is required"))
        
    # Get all student groups for the student
    groups = frappe.db.sql("""
        SELECT parent 
        FROM `tabStudent Group Student` 
        WHERE student = %s
    """, (student_name,), as_dict=True)
    
    group_names = [g['parent'] for g in groups]
    
    if not group_names:
        return []
        
    placeholders = ', '.join(['%s'] * len(group_names))
    query = f"""
        SELECT 
            cs.name,
            cs.course,
            cs.student_group,
            cs.instructor_name,
            cs.schedule_date,
            cs.from_time,
            cs.to_time,
            cs.room,
            c.course_name,
            cs.color as color
        FROM `tabCourse Schedule` cs
        LEFT JOIN `tabCourse` c ON cs.course = c.name
        WHERE cs.student_group IN ({placeholders})
          AND cs.docstatus = 0
    """
    
    # Wait, docstatus = 0? In test data, the schedules are docstatus 0 (Draft).
    # I should allow docstatus < 2 just in case.
    query = f"""
        SELECT 
            cs.name,
            cs.course,
            cs.student_group,
            cs.instructor_name,
            cs.schedule_date,
            cs.from_time,
            cs.to_time,
            cs.room,
            c.course_name,
            cs.color as color
        FROM `tabCourse Schedule` cs
        LEFT JOIN `tabCourse` c ON cs.course = c.name
        WHERE cs.student_group IN ({placeholders})
          AND cs.docstatus < 2
    """
    
    args = list(group_names)
    
    if date_start:
        query += " AND cs.schedule_date >= %s"
        args.append(date_start)
    if date_end:
        query += " AND cs.schedule_date <= %s"
        args.append(date_end)
        
    query += " ORDER BY cs.schedule_date ASC, cs.from_time ASC"
    
    schedules = frappe.db.sql(query, tuple(args), as_dict=True)
    
    return schedules
