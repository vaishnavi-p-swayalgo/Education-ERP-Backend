import frappe
from frappe import _
import string
import random

def generate_random_digits(n=2):
    return ''.join(random.choices(string.digits, k=n))

@frappe.whitelist()
def generate_teacher_accounts():
    frappe.only_for("System Manager")
    
    # Get all teachers without user accounts
    teachers = frappe.db.sql("""
        SELECT name, employee_name, first_name, last_name
        FROM `tabEmployee`
        WHERE designation = 'Teacher' 
          AND (user_id IS NULL OR user_id = '')
          AND status = 'Active'
    """, as_dict=True)

    generated = 0
    from frappe.model.naming import make_autoname
    for teacher in teachers:
        first = (teacher.first_name or teacher.employee_name or "tch").lower().strip().replace(" ", "")
        last = (teacher.last_name or "").lower().strip().replace(" ", "")
        base_name = f"{first}_{last}" if last else first
        
        seq = make_autoname("EMP-.####").split("-")[1]
        username = f"{base_name}_{seq}"
        email = f"tch_{username}@school.local"
        
        name_prefix = (teacher.first_name or teacher.employee_name or "Tch")[:3].capitalize()
        sys_pwd = f"{name_prefix}{teacher.name}@{generate_random_digits(2)}"
        
        user = create_user(
            email=email,
            username=username,
            first_name=teacher.employee_name,
            role="Instructor",
            sys_pwd=sys_pwd
        )
        
        # Link user to employee
        frappe.db.set_value("Employee", teacher.name, "user_id", email)
        generated += 1
        
    return {"status": "success", "generated": generated}


@frappe.whitelist()
def generate_student_accounts(standards=None):
    frappe.only_for("System Manager")
    
    if isinstance(standards, str):
        import json
        standards = json.loads(standards)
        
    if not standards:
        return {"status": "error", "message": "No standards provided"}
        
    # Get all admitted students in these standards without user accounts
    # Frappe Student natively has student_email_id which is used for the portal
    # But to ensure they don't have accounts, we check if a User with their username exists
    
    placeholders = ', '.join(['%s'] * len(standards))
    
    # Frappe Student natively links to Program via `tabProgram Enrollment`
    students = frappe.db.sql(f"""
        SELECT s.name, s.student_name, s.first_name, s.last_name, s.student_email_id
        FROM `tabProgram Enrollment` pe
        JOIN `tabStudent` s ON pe.student = s.name
        WHERE pe.program IN ({placeholders})
          AND pe.docstatus = 1
          AND (s.student_email_id IS NULL OR s.student_email_id = '')
    """, tuple(standards), as_dict=True)

    generated = 0
    from frappe.model.naming import make_autoname
    for student in students:
        first = (student.first_name or student.student_name or "stu").lower().strip().replace(" ", "")
        last = (student.last_name or "").lower().strip().replace(" ", "")
        base_name = f"{first}_{last}" if last else first
        
        # Start at 0100
        raw_seq = make_autoname("STU-.####").split("-")[1]
        seq = f"{int(raw_seq) + 99:04d}"
        
        username = f"{base_name}_{seq}"
        email = f"stu_{username}@school.local"
        
        name_prefix = (student.first_name or student.student_name or "Stu")[:3].capitalize()
        sys_pwd = f"{name_prefix}{student.name}${generate_random_digits(2)}"
        
        user = create_user(
            email=email,
            username=username,
            first_name=student.student_name,
            role="Student",
            sys_pwd=sys_pwd
        )
        
        frappe.db.set_value("Student", student.name, "student_email_id", email)
        generated += 1
        
    return {"status": "success", "generated": generated}


@frappe.whitelist()
def generate_guardian_accounts():
    frappe.only_for("System Manager")
    
    guardians = frappe.db.sql("""
        SELECT name, guardian_name, email_address
        FROM `tabGuardian`
        WHERE user IS NULL OR user = ''
    """, as_dict=True)

    generated = 0
    from frappe.model.naming import make_autoname
    for guard in guardians:
        # Guardian doctype may not have first_name/last_name separated, so we split guardian_name
        parts = (guard.guardian_name or "guardian").split()
        first = parts[0].lower().strip()
        last = parts[-1].lower().strip() if len(parts) > 1 else ""
        base_name = f"{first}_{last}" if last else first
        
        seq = make_autoname("GRD-.####").split("-")[1]
        username = f"{base_name}_{seq}"
        email = f"grd_{username}@school.local"
        
        sys_pwd = f"Guard{guard.name}#{generate_random_digits(2)}"
        
        # Check if user already exists
        if frappe.db.exists("User", email):
            frappe.db.set_value("Guardian", guard.name, "user", email)
            continue
            
        user = create_user(
            email=email,
            username=username,
            first_name=guard.guardian_name,
            role="Guardian",
            sys_pwd=sys_pwd
        )
        
        frappe.db.set_value("Guardian", guard.name, "user", email)
        generated += 1
        
    return {"status": "success", "generated": generated}


@frappe.whitelist()
def get_all_accounts():
    frappe.only_for("System Manager")
    
    users = frappe.db.sql("""
        SELECT name as email, username, full_name, system_password, user_set_password, first_login_done, enabled
        FROM `tabUser`
        WHERE (name LIKE 'tch_%@school.local' 
            OR name LIKE 'stu_%@school.local' 
            OR name LIKE 'grd_%@school.local' 
            OR name LIKE 'hr_%@school.local' 
            OR name LIKE 'acc_%@school.local')
    """, as_dict=True)
    return users


@frappe.whitelist(allow_guest=True)
def set_first_password(new_password):
    # This endpoint is called when user first logs in
    if frappe.session.user == "Guest":
        frappe.throw(_("Not logged in"))
        
    user = frappe.get_doc("User", frappe.session.user)
    
    if user.first_login_done:
        # Already done, maybe they are just changing password, but for now we only handle first login
        pass
        
    # Set the new password via auth wrapper
    from frappe.core.doctype.user.user import update_password
    update_password(new_password=new_password, logout_all_sessions=False)
    
    # Update custom fields
    user.db_set("user_set_password", new_password)
    user.db_set("first_login_done", 1)
    
    return {"status": "success"}


def create_user(email, username, first_name, role, sys_pwd):
    if frappe.db.exists("User", email):
        return frappe.get_doc("User", email)
        
    user = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": first_name,
        "username": username,
        "send_welcome_email": 0,
        "system_password": sys_pwd,
        "first_login_done": 0,
        "new_password": sys_pwd
    })
    user.flags.ignore_permissions = True
    user.flags.ignore_password_policy = True
    user.insert(ignore_permissions=True)
    
    # Assign Role
    user.add_roles(role)
    
    return user
@frappe.whitelist()
def create_employee(first_name, gender, date_of_birth, date_of_joining, middle_name=None, last_name=None, department=None, designation=None):
    frappe.only_for("System Manager")
    
    # Get default company
    companies = frappe.get_all("Company", pluck="name")
    company = companies[0] if companies else None
    
    if not company:
        frappe.throw("No Company found in the system.")
        
    emp = frappe.get_doc({
        "doctype": "Employee",
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "gender": gender,
        "date_of_birth": date_of_birth,
        "date_of_joining": date_of_joining,
        "department": department,
        "designation": designation,
        "company": company,
        "status": "Active"
    })
    emp.insert(ignore_permissions=True)
    return {"status": "success", "employee_id": emp.name}


@frappe.whitelist()
def get_eligible_employees():
    frappe.only_for("System Manager")
    
    # Get all employees
    employees = frappe.db.get_all("Employee", fields=["name", "employee_name", "designation", "department", "gender"], filters={"status": "Active"})
    
    # Exclude those who are already Instructors
    instructors = frappe.db.get_all("Instructor", pluck="employee")
    
    # For HR, check designation
    eligible_for_teacher = [e for e in employees if e.name not in instructors]
    eligible_for_hr = [e for e in employees if e.designation != "HR"]
    
    return {
        "status": "success",
        "eligible_for_teacher": eligible_for_teacher,
        "eligible_for_hr": eligible_for_hr
    }

@frappe.whitelist()
def create_instructor(employee_id):
    frappe.only_for("System Manager")
    
    emp = frappe.get_doc("Employee", employee_id)
    
    instructor = frappe.get_doc({
        "doctype": "Instructor",
        "instructor_name": emp.employee_name,
        "employee": emp.name,
        "gender": emp.gender,
        "status": "Active"
    })
    instructor.insert(ignore_permissions=True)
    
    # Also set their designation to Teacher if not set
    if not emp.designation:
        emp.db_set("designation", "Teacher")
        
    return {"status": "success", "instructor_id": instructor.name}

@frappe.whitelist()
def assign_hr_role(employee_id):
    frappe.only_for("System Manager")
    
    emp = frappe.get_doc("Employee", employee_id)
    
    # Create HR designation if it doesn't exist
    if not frappe.db.exists("Designation", "HR"):
        desig = frappe.get_doc({
            "doctype": "Designation",
            "designation_name": "HR"
        })
        desig.insert(ignore_permissions=True)
        
    emp.db_set("designation", "HR")
    return {"status": "success"}


@frappe.whitelist()
def create_guardian(guardian_name, email_address, mobile_number):
    frappe.only_for("System Manager")
    
    guardian = frappe.get_doc({
        "doctype": "Guardian",
        "guardian_name": guardian_name,
        "email_address": email_address,
        "mobile_number": mobile_number
    })
    guardian.insert(ignore_permissions=True)
    return {"status": "success", "guardian_id": guardian.name}

@frappe.whitelist()
def get_employees_list():
    frappe.only_for("System Manager")
    return frappe.get_all("Employee", fields=["name", "employee_name", "gender", "department", "designation", "status", "date_of_joining"])

@frappe.whitelist()
def get_teachers_list():
    frappe.only_for("System Manager")
    return frappe.get_all("Instructor", fields=["name", "instructor_name", "employee", "department", "status"])

@frappe.whitelist()
def get_hr_list():
    frappe.only_for("System Manager")
    return frappe.get_all("Employee", fields=["name", "employee_name", "gender", "department", "designation", "status", "date_of_joining"], filters={"designation": "HR"})

@frappe.whitelist()
def get_guardians_list():
    frappe.only_for("System Manager")
    return frappe.get_all("Guardian", fields=["name", "guardian_name", "email_address", "mobile_number"])
