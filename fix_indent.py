import os, re

templates = [
    'main_app/templates/hod_template/student_feedback_template.html',
    'main_app/templates/hod_template/staff_leave_view.html',
    'main_app/templates/hod_template/student_leave_view.html',
    'main_app/templates/hod_template/student_notification.html',
    'main_app/templates/hod_template/staff_notification.html',
    'main_app/templates/student_template/student_feedback.html',
    'main_app/templates/student_template/student_view_result.html',
    'main_app/templates/student_template/student_apply_leave.html',
    'main_app/templates/student_template/student_view_notification.html',
    'main_app/templates/staff_template/staff_view_notification.html',
    'main_app/templates/staff_template/staff_feedback.html',
    'main_app/templates/staff_template/staff_apply_leave.html',
]

for path in templates:
    if not os.path.exists(path):
        print(f"SKIP: {path}")
        continue
    with open(path, 'r') as f:
        content = f.read()
    
    # Fix pattern: <div class="table-responsive">\n<table  =>  <div class="table-responsive">\n                            <table
    # Only fix lines where <table is at column 0 right after table-responsive
    lines = content.split('\n')
    changed = False
    for i in range(len(lines)):
        stripped = lines[i].lstrip()
        if stripped.startswith('<table') and 'class="table' in stripped:
            # Check if previous non-empty line has table-responsive
            for j in range(i-1, max(0, i-3), -1):
                if 'table-responsive' in lines[j]:
                    # Get the indentation of the table-responsive line
                    indent = len(lines[j]) - len(lines[j].lstrip())
                    new_indent = ' ' * (indent + 4)
                    if not lines[i].startswith(new_indent):
                        lines[i] = new_indent + stripped
                        changed = True
                    break
        # Fix closing </div> at column 0 that should match table-responsive
        if stripped == '</div>' and lines[i] == '</div>':
            # Check if there's a </table> above it
            for j in range(i-1, max(0, i-3), -1):
                if '</table>' in lines[j]:
                    indent_of_table_close = len(lines[j]) - len(lines[j].lstrip())
                    new_indent = ' ' * indent_of_table_close
                    lines[i] = new_indent + '</div>'
                    changed = True
                    break
    
    if changed:
        with open(path, 'w') as f:
            f.write('\n'.join(lines))
        print(f"FIXED: {path}")
    else:
        print(f"OK: {path}")

