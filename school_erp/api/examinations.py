import frappe
import json

@frappe.whitelist()
def bulk_create_exam_schedule(payload):
    frappe.only_for("System Manager")
    
    data = json.loads(payload)
    
    academic_term = data.get("academic_term")
    assessment_group = data.get("assessment_group")
    program = data.get("program")
    grading_scale = data.get("grading_scale")
    schedule = data.get("schedule", [])
    
    if not all([academic_term, assessment_group, program, grading_scale, schedule]):
        return {"status": "error", "message": "Missing mandatory fields for exam schedule creation."}
    
    # We will fetch groups per subject intelligently
    created_count = 0
    
    for subj in schedule:
        course = subj.get("course")
        
        # 1. Try to find Course-specific Student Groups for this subject
        groups = frappe.db.get_all(
            "Student Group", 
            filters={"program": program, "group_based_on": "Course", "course": course}, 
            pluck="name"
        )
        
        # 2. If no course-specific groups exist, fallback to general Batch divisions
        if not groups:
            groups = frappe.db.get_all(
                "Student Group", 
                filters={"program": program, "group_based_on": "Batch"}, 
                pluck="name"
            )
            
        if not groups:
            continue # No valid student groups found for this subject/program
            
        for group in groups:
            # check if exists
            exists = frappe.db.exists("Assessment Plan", {
                "student_group": group,
                "course": course,
                "assessment_group": assessment_group,
                "academic_term": academic_term
            })
            if exists: 
                continue
            
            doc = frappe.get_doc({
                "doctype": "Assessment Plan",
                "student_group": group,
                "course": course,
                "assessment_group": assessment_group,
                "grading_scale": grading_scale,
                "program": program,
                "academic_term": academic_term,
                "schedule_date": subj.get("schedule_date"),
                "from_time": subj.get("from_time"),
                "to_time": subj.get("to_time"),
                "maximum_assessment_score": float(subj.get("maximum_score") or 100),
                "assessment_name": f"{assessment_group} - {course} - {group}"
            })
            
            # Frappe requires assessment_criteria to sum up to maximum_assessment_score
            default_criteria = "Theory Exam"
            if not frappe.db.exists("Assessment Criteria", default_criteria):
                frappe.get_doc({
                    "doctype": "Assessment Criteria",
                    "assessment_criteria": default_criteria
                }).insert(ignore_permissions=True)
                
            doc.append("assessment_criteria", {
                "assessment_criteria": default_criteria,
                "maximum_score": float(subj.get("maximum_score") or 100)
            })
            
            doc.insert(ignore_permissions=True)
            doc.submit()
            
            # Force update academic_term to bypass 'fetch_from' logic
            frappe.db.set_value("Assessment Plan", doc.name, "academic_term", academic_term)
            
            created_count += 1
            
    return {"status": "success", "created": created_count}

@frappe.whitelist()
def get_exam_schedules():
    frappe.only_for("System Manager")
    
    plans = frappe.db.sql("""
        SELECT 
            assessment_group, academic_term, program,
            COUNT(DISTINCT course) as subject_count,
            MIN(schedule_date) as start_date,
            MAX(schedule_date) as end_date,
            MAX(grading_scale) as grading_scale
        FROM `tabAssessment Plan`
        WHERE docstatus = 1
        GROUP BY assessment_group, academic_term, program
        ORDER BY start_date DESC
    """, as_dict=True)
    return plans

@frappe.whitelist()
def get_marks_entry_dashboard():
    frappe.only_for("System Manager")
    
    # Get all submitted Assessment Plans
    plans = frappe.get_all(
        "Assessment Plan", 
        filters={"docstatus": 1},
        fields=["name", "assessment_name", "student_group", "course", "assessment_group", 
                "schedule_date", "custom_marks_entry_status", "custom_marks_deadline", "program"],
        order_by="schedule_date desc"
    )
    
    # Calculate submission stats for each
    for p in plans:
        # total students in student group
        total_students = frappe.db.count("Student Group Student", {"parent": p.student_group})
        # total results submitted for this plan
        submitted_results = frappe.db.count("Assessment Result", {"assessment_plan": p.name, "docstatus": 1})
        
        p["total_students"] = total_students
        p["submitted_results"] = submitted_results
        
    return plans

@frappe.whitelist()
def update_marks_entry_status(plan_name, status, deadline=None):
    frappe.only_for("System Manager")
    
    if not frappe.db.exists("Assessment Plan", plan_name):
        frappe.throw("Assessment Plan not found")
        
    frappe.db.set_value("Assessment Plan", plan_name, "custom_marks_entry_status", status)
    if deadline:
        frappe.db.set_value("Assessment Plan", plan_name, "custom_marks_deadline", deadline)
        
    return {"status": "success"}
