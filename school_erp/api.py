import frappe

@frappe.whitelist()
def get_student_group_counts():
    """
    Returns the count of active students in each Student Group.
    Since Frappe restricts direct REST API access to the child table `Student Group Student`,
    this whitelist method safely provides the aggregate counts for the frontend.
    """
    counts = frappe.db.sql("""
        SELECT parent as group_name, COUNT(name) as count
        FROM `tabStudent Group Student`
        WHERE active = 1
        GROUP BY parent
    """, as_dict=True)
    return {row.group_name: row.count for row in counts}
