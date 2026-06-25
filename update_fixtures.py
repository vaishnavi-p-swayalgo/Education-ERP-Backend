import os
import json

# Remove fixtures from education hooks.py
edu_hooks_path = '/home/lenovo/edu-bench/apps/education/education/hooks.py'
with open(edu_hooks_path, 'r') as f:
    lines = f.readlines()

new_lines = [line for line in lines if not line.startswith('fixtures = [{"dt": "Custom Field"')]
with open(edu_hooks_path, 'w') as f:
    f.writelines(new_lines)
print("Cleaned education hooks.py")

# Add Custom DocPerm fixture to school_erp hooks.py
school_hooks_path = '/home/lenovo/edu-bench/apps/school_erp/school_erp/hooks.py'
with open(school_hooks_path, 'r') as f:
    school_content = f.read()

# Since school_erp already has a fixtures list, I will use Python AST to safely append it, or just do a string replace since I know exactly what it looks like.
if '{"dt": "Custom DocPerm", "filters": [["parent", "in", ["Student Applicant", "Student"]]]}' not in school_content:
    # Append to the existing fixtures array. I will find `fixtures = [\n`
    new_content = school_content.replace('fixtures = [\n', 'fixtures = [\n    {"dt": "Custom DocPerm", "filters": [["parent", "in", ["Student Applicant", "Student"]]]},\n')
    with open(school_hooks_path, 'w') as f:
        f.write(new_content)
    print("Added Custom DocPerm to school_erp hooks.py")
