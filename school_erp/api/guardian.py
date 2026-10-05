import frappe
import datetime
import calendar

@frappe.whitelist()
def get_children(guardian_email=None):
    # The frontend uses a static API key, so frappe.session.user is Administrator.
    # We must rely on guardian_email passed from the frontend.
    lookup_user = guardian_email if guardian_email else frappe.session.user
    
    # The frontend might pass the username (e.g., 'ganpat_padwal_0001') instead of the email.
    user_email = frappe.db.get_value("User", {"username": lookup_user}, "email") or lookup_user
    
    guardian = frappe.db.get_value("Guardian", {"user": user_email}, "name")
    if not guardian:
        return []
    
    students = []
    
    # Check Guardian Student table
    guardian_students = frappe.get_all("Guardian Student", filters={"parent": guardian}, fields=["student", "student_name"])
    for gs in guardian_students:
        students.append({"student": gs.student, "student_name": gs.student_name})
        
    # Check Student Guardian table
    student_guardians = frappe.get_all("Student Guardian", filters={"guardian": guardian}, fields=["parent", "guardian_name"])
    for sg in student_guardians:
        if not any(s['student'] == sg.parent for s in students):
            student_name = frappe.db.get_value("Student", sg.parent, "student_name")
            students.append({"student": sg.parent, "student_name": student_name})
            
    for s in students:
        s_doc = frappe.get_doc("Student", s['student'])
        s['image'] = s_doc.image
        s['joining_date'] = s_doc.joining_date
        
        enrollment = frappe.db.get_value("Program Enrollment", 
            {"student": s['student'], "docstatus": 1}, 
            ["program", "academic_year"], as_dict=True)
        
        student_group = frappe.db.get_value("Student Group Student", {"student": s['student'], "active": 1}, "parent")
        
        if enrollment:
            s['program'] = enrollment.program
            s['academic_year'] = enrollment.academic_year
        if student_group:
            s['student_group'] = student_group
            
    return students


@frappe.whitelist()
def get_dashboard_summary(student):
    now = datetime.datetime.now()
    month_start = now.replace(day=1)
    
    attendance = frappe.get_all("Student Attendance", 
        filters={"student": student, "date": [">=", month_start], "docstatus": 1},
        fields=["status"])
        
    total_days = len(attendance)
    present_days = len([a for a in attendance if a.status == "Present"])
    attendance_pct = (present_days / total_days * 100) if total_days > 0 else 100
    
    latest_result = frappe.get_all("Assessment Result",
        filters={"student": student, "docstatus": 1},
        fields=["assessment_plan", "course", "total_score", "maximum_score", "grade", "creation"],
        order_by="creation desc", limit=1)
        
    last_exam = latest_result[0] if latest_result else None
    if last_exam and last_exam.maximum_score:
        last_exam.pct = round((last_exam.total_score / last_exam.maximum_score) * 100, 1)
    
    today = now.date()
    today_att = frappe.db.get_value("Student Attendance", {"student": student, "date": today, "docstatus": 1}, "status")
    
    fees = frappe.db.sql("""
        SELECT SUM(outstanding_amount) as due
        FROM `tabFees`
        WHERE student = %s AND docstatus = 1
    """, (student,), as_dict=True)
    fees_due = fees[0].due if fees and fees[0].due else 0
    
    enrollments = frappe.get_all("Student Group Student", {"student": student, "active": 1}, pluck="parent")
    homework = frappe.get_all("Student Homework",
        filters={"student_group": ["in", enrollments], "due_date": [">=", today]},
        fields=["title", "due_date"],
        order_by="due_date asc", limit=3) if enrollments else []
        
    return {
        "attendance_pct": round(attendance_pct, 1),
        "last_exam": last_exam,
        "today_attendance": today_att,
        "fees_due": fees_due,
        "upcoming_homework": homework
    }

@frappe.whitelist()
def get_attendance_log(student, month, year):
    start_date = f"{year}-{int(month):02d}-01"
    last_day = calendar.monthrange(int(year), int(month))[1]
    end_date = f"{year}-{int(month):02d}-{last_day}"
    
    attendance = frappe.get_all("Student Attendance",
        filters={"student": student, "date": ["between", [start_date, end_date]], "docstatus": 1},
        fields=["date", "status", "leave_application", "student_group", "course_schedule"])
        
    return attendance

@frappe.whitelist()
def get_marks_report(student):
    results = frappe.get_all("Assessment Result",
        filters={"student": student, "docstatus": 1},
        fields=["name", "assessment_plan", "course", "total_score", "maximum_score", "grade", "creation"],
        order_by="creation desc")
    
    for r in results:
        r.pct = (r.total_score / r.maximum_score * 100) if r.maximum_score else 0
        r.insight = f"Scored {round(r.pct, 1)}% in {r.course}. "
        if r.pct > 80:
            r.insight += "Excellent performance."
        elif r.pct > 60:
            r.insight += "Good performance."
        else:
            r.insight += "Needs attention."
            
    return results

@frappe.whitelist()
def get_homework(student):
    enrollments = frappe.get_all("Student Group Student", {"student": student, "active": 1}, pluck="parent")
    if not enrollments:
        return []
        
    hw = frappe.get_all("Student Homework",
        filters={"student_group": ["in", enrollments]},
        fields=["name", "title", "description", "due_date", "status", "attachment", "instructor"],
        order_by="due_date desc")
    
    for h in hw:
        h.instructor_name = frappe.db.get_value("Instructor", h.instructor, "instructor_name") if h.instructor else ""
        
    return hw

@frappe.whitelist()
def get_timetable(student, date_start=None, date_end=None):
    enrollments = frappe.get_all("Student Group Student", {"student": student, "active": 1}, pluck="parent")
    if not enrollments:
        return []
        
    if date_start and date_end:
        start_of_week = date_start
        end_of_week = date_end
    else:
        today = datetime.datetime.now().date()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=6)
    
    schedule = frappe.get_all("Course Schedule",
        filters={"student_group": ["in", enrollments], "schedule_date": ["between", [start_of_week, end_of_week]], "docstatus": ["<", 2]},
        fields=["name", "title", "course", "instructor_name", "schedule_date", "from_time", "to_time", "room", "color"])
        
    return schedule

@frappe.whitelist()
def get_exams(student):
    enrollments = frappe.get_all("Student Group Student", {"student": student, "active": 1}, pluck="parent")
    if not enrollments:
        return []
        
    today = datetime.datetime.now().date()
    
    exams = frappe.get_all("Assessment Plan",
        filters={"student_group": ["in", enrollments], "schedule_date": [">=", today], "docstatus": 1},
        fields=["name", "assessment_name", "course", "assessment_group", "schedule_date", "from_time", "to_time", "maximum_assessment_score", "room"],
        order_by="schedule_date asc")
        
    return exams
