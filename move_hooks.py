import os

# Clean up education hooks.py
edu_hooks_path = '/home/lenovo/edu-bench/apps/education/education/hooks.py'
with open(edu_hooks_path, 'r') as f:
    edu_content = f.read()

# I appended the following to education hooks:
doc_events_str = """
doc_events = {
	"Student Applicant": {
		"validate": "education.admissions_hooks.validate_student_applicant",
		"on_update": "education.admissions_hooks.on_update_student_applicant"
	}
}
"""
if doc_events_str in edu_content:
    edu_content = edu_content.replace(doc_events_str, '')
    with open(edu_hooks_path, 'w') as f:
        f.write(edu_content)
    print("Removed doc_events from education hooks.py")

# Add to school_erp hooks.py
school_hooks_path = '/home/lenovo/edu-bench/apps/school_erp/school_erp/hooks.py'
with open(school_hooks_path, 'r') as f:
    school_content = f.read()

new_doc_events_str = """
doc_events = {
	"Student Applicant": {
		"validate": "school_erp.admissions_hooks.validate_student_applicant",
		"on_update": "school_erp.admissions_hooks.on_update_student_applicant"
	}
}
"""
if "doc_events = {" not in school_content or "# doc_events = {" in school_content:
    with open(school_hooks_path, 'a') as f:
        f.write(new_doc_events_str)
    print("Added doc_events to school_erp hooks.py")
