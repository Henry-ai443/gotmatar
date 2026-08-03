import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

base_path = "accounting/templates/"

# manage_fee_category.html
write_file(base_path + "hod_template/accounting/manage_fee_category.html", """{% extends 'main_app/base.html' %}
{% block page_title %}{{page_title}}{% endblock page_title %}
{% block content %}
<section class="content">
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-4">
                <div class="card card-primary">
                    <div class="card-header"><h3 class="card-title">Add Fee Category</h3></div>
                    <form role="form" method="POST">
                        {% csrf_token %}
                        <div class="card-body">
                            {{ form.as_p }}
                        </div>
                        <div class="card-footer">
                            <button type="submit" class="btn btn-primary">Save Category</button>
                        </div>
                    </form>
                </div>
            </div>
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header"><h3 class="card-title">Fee Categories</h3></div>
                    <div class="card-body">
                        <table class="table table-bordered table-hover">
                            <thead class="thead-dark"><tr><th>#</th><th>Name</th><th>Recurring</th><th>Actions</th></tr></thead>
                            <tbody>
                                {% for category in categories %}
                                <tr>
                                    <td>{{ forloop.counter }}</td>
                                    <td>{{ category.name }}</td>
                                    <td>{{ category.is_recurring|yesno:"Yes,No" }}</td>
                                    <td>
                                        <a href="{% url 'edit_fee_category' category.id %}" class="btn btn-sm btn-info">Edit</a>
                                        <a href="{% url 'delete_fee_category' category.id %}" class="btn btn-sm btn-danger" onclick="return confirm('Delete?');">Delete</a>
                                    </td>
                                </tr>
                                {% empty %}
                                <tr><td colspan="4">No Fee Categories Found</td></tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>
{% endblock content %}""")

# edit_fee_category.html
write_file(base_path + "hod_template/accounting/edit_fee_category.html", """{% extends 'main_app/base.html' %}
{% block page_title %}{{page_title}}{% endblock page_title %}
{% block content %}
<section class="content">
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-12">
                <div class="card card-primary">
                    <div class="card-header"><h3 class="card-title">Edit Fee Category</h3></div>
                    <form role="form" method="POST">
                        {% csrf_token %}
                        <div class="card-body">
                            {{ form.as_p }}
                        </div>
                        <div class="card-footer">
                            <button type="submit" class="btn btn-primary">Update Category</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</section>
{% endblock content %}""")


# manage_fee_structure.html
write_file(base_path + "hod_template/accounting/manage_fee_structure.html", """{% extends 'main_app/base.html' %}
{% block page_title %}{{page_title}}{% endblock page_title %}
{% block content %}
<section class="content">
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-4">
                <div class="card card-primary">
                    <div class="card-header"><h3 class="card-title">Add Fee Structure</h3></div>
                    <form role="form" method="POST">
                        {% csrf_token %}
                        <div class="card-body">{{ form.as_p }}</div>
                        <div class="card-footer">
                            <button type="submit" class="btn btn-primary">Save Structure</button>
                        </div>
                    </form>
                </div>
            </div>
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header"><h3 class="card-title">Fee Structures</h3></div>
                    <div class="card-body">
                        <table class="table table-bordered table-hover">
                            <thead class="thead-dark"><tr><th>#</th><th>Course</th><th>Session</th><th>Category</th><th>Amount</th><th>Actions</th></tr></thead>
                            <tbody>
                                {% for struct in structures %}
                                <tr>
                                    <td>{{ forloop.counter }}</td>
                                    <td>{{ struct.course.name }}</td>
                                    <td>{{ struct.session }}</td>
                                    <td>{{ struct.category.name }}</td>
                                    <td>${{ struct.amount }}</td>
                                    <td>
                                        <a href="{% url 'edit_fee_structure' struct.id %}" class="btn btn-sm btn-info">Edit</a>
                                        <a href="{% url 'delete_fee_structure' struct.id %}" class="btn btn-sm btn-danger" onclick="return confirm('Delete?');">Delete</a>
                                    </td>
                                </tr>
                                {% empty %}
                                <tr><td colspan="6">No Fee Structures Found</td></tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>
{% endblock content %}""")

# edit_fee_structure.html
write_file(base_path + "hod_template/accounting/edit_fee_structure.html", """{% extends 'main_app/base.html' %}
{% block page_title %}{{page_title}}{% endblock page_title %}
{% block content %}
<section class="content">
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-12">
                <div class="card card-primary">
                    <div class="card-header"><h3 class="card-title">Edit Fee Structure</h3></div>
                    <form role="form" method="POST">
                        {% csrf_token %}
                        <div class="card-body">
                            {{ form.as_p }}
                        </div>
                        <div class="card-footer">
                            <button type="submit" class="btn btn-primary">Update Structure</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</section>
{% endblock content %}""")


# manage_salary_structure.html
write_file(base_path + "hod_template/accounting/manage_salary_structure.html", """{% extends 'main_app/base.html' %}
{% block page_title %}{{page_title}}{% endblock page_title %}
{% block content %}
<section class="content">
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-4">
                <div class="card card-primary">
                    <div class="card-header"><h3 class="card-title">Add / Update Salary</h3></div>
                    <form role="form" method="POST">
                        {% csrf_token %}
                        <div class="card-body">{{ form.as_p }}</div>
                        <div class="card-footer">
                            <button type="submit" class="btn btn-primary">Save Salary</button>
                        </div>
                    </form>
                </div>
            </div>
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header"><h3 class="card-title">Salary Structures</h3></div>
                    <div class="card-body">
                        <table class="table table-bordered table-hover">
                            <thead class="thead-dark"><tr><th>Staff</th><th>Basic</th><th>Allowances</th><th>Effective From</th></tr></thead>
                            <tbody>
                                {% for struct in structures %}
                                <tr>
                                    <td>{{ struct.staff.admin.first_name }} {{ struct.staff.admin.last_name }}</td>
                                    <td>${{ struct.basic_salary }}</td>
                                    <td>${{ struct.allowances }}</td>
                                    <td>{{ struct.effective_from }}</td>
                                </tr>
                                {% empty %}
                                <tr><td colspan="4">No Salary Structures Found</td></tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>
{% endblock content %}""")


# manage_payslips.html
write_file(base_path + "hod_template/accounting/manage_payslips.html", """{% extends 'main_app/base.html' %}
{% block page_title %}{{page_title}}{% endblock page_title %}
{% block content %}
<section class="content">
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-4">
                <div class="card card-primary">
                    <div class="card-header"><h3 class="card-title">Generate Payslip</h3></div>
                    <form role="form" method="POST">
                        {% csrf_token %}
                        <div class="card-body">{{ form.as_p }}</div>
                        <div class="card-footer">
                            <button type="submit" class="btn btn-primary">Generate</button>
                        </div>
                    </form>
                </div>
            </div>
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header"><h3 class="card-title">All Payslips</h3></div>
                    <div class="card-body">
                        <table class="table table-bordered table-hover">
                            <thead class="thead-dark"><tr><th>Staff</th><th>Month/Year</th><th>Gross</th><th>Net</th><th>Status</th><th>Actions</th></tr></thead>
                            <tbody>
                                {% for p in payslips %}
                                <tr>
                                    <td>{{ p.staff.admin.first_name }} {{ p.staff.admin.last_name }}</td>
                                    <td>{{ p.month }}/{{ p.year }}</td>
                                    <td>${{ p.gross }}</td>
                                    <td>${{ p.net_pay }}</td>
                                    <td>
                                        {% if p.status == 'draft' %}<span class="badge badge-warning">Draft</span>{% else %}<span class="badge badge-success">Paid</span>{% endif %}
                                    </td>
                                    <td>
                                        {% if p.status == 'draft' %}
                                        <a href="{% url 'mark_payslip_paid' p.id %}" class="btn btn-sm btn-success" onclick="return confirm('Mark as paid?');">Mark Paid</a>
                                        {% endif %}
                                    </td>
                                </tr>
                                {% empty %}
                                <tr><td colspan="6">No Payslips Found</td></tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>
{% endblock content %}""")

# view_invoices.html
write_file(base_path + "hod_template/accounting/view_invoices.html", """{% extends 'main_app/base.html' %}
{% block page_title %}{{page_title}}{% endblock page_title %}
{% block content %}
<section class="content">
    <div class="container-fluid">
        <div class="card">
            <div class="card-header"><h3 class="card-title">Student Invoices</h3></div>
            <div class="card-body">
                <table class="table table-bordered table-hover">
                    <thead class="thead-dark"><tr><th>Student</th><th>Session</th><th>Total</th><th>Due Date</th><th>Status</th><th>Actions</th></tr></thead>
                    <tbody>
                        {% for invoice in invoices %}
                        <tr>
                            <td>{{ invoice.student.admin.first_name }} {{ invoice.student.admin.last_name }}</td>
                            <td>{{ invoice.session }}</td>
                            <td>${{ invoice.total_amount }}</td>
                            <td>{{ invoice.due_date }}</td>
                            <td>
                                {% if invoice.status == 'paid' %}<span class="badge badge-success">Paid</span>
                                {% elif invoice.status == 'partial' %}<span class="badge badge-warning">Partial</span>
                                {% elif invoice.status == 'overdue' %}<span class="badge badge-danger">Overdue</span>
                                {% else %}<span class="badge badge-secondary">Unpaid</span>{% endif %}
                            </td>
                            <td>
                                {% if invoice.status != 'paid' %}
                                <a href="{% url 'record_payment' invoice.id %}" class="btn btn-sm btn-primary">Record Payment</a>
                                {% endif %}
                            </td>
                        </tr>
                        {% empty %}
                        <tr><td colspan="6">No Invoices Found</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</section>
{% endblock content %}""")

# record_payment.html
write_file(base_path + "hod_template/accounting/record_payment.html", """{% extends 'main_app/base.html' %}
{% block page_title %}{{page_title}}{% endblock page_title %}
{% block content %}
<section class="content">
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-6 offset-md-3">
                <div class="card card-success">
                    <div class="card-header"><h3 class="card-title">Record Payment for {{ invoice.student.admin.first_name }} (Total: ${{ invoice.total_amount }})</h3></div>
                    <form role="form" method="POST">
                        {% csrf_token %}
                        <div class="card-body">{{ form.as_p }}</div>
                        <div class="card-footer"><button type="submit" class="btn btn-success">Save Payment</button></div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</section>
{% endblock content %}""")

# accounting_reports.html
write_file(base_path + "hod_template/accounting/accounting_reports.html", """{% extends 'main_app/base.html' %}
{% block page_title %}{{page_title}}{% endblock page_title %}
{% block content %}
<section class="content">
    <div class="container-fluid">
        <div class="row">
            <div class="col-lg-4 col-6">
                <div class="small-box bg-success">
                    <div class="inner"><h3>${{ total_collected }}</h3><p>Total Collected</p></div>
                    <div class="icon"><i class="fas fa-money-bill-wave"></i></div>
                </div>
            </div>
            <div class="col-lg-4 col-6">
                <div class="small-box bg-danger">
                    <div class="inner"><h3>${{ outstanding_fees }}</h3><p>Outstanding Fees</p></div>
                    <div class="icon"><i class="fas fa-exclamation-circle"></i></div>
                </div>
            </div>
            <div class="col-lg-4 col-6">
                <div class="small-box bg-info">
                    <div class="inner"><h3>${{ total_payroll }}</h3><p>Total Payroll Paid</p></div>
                    <div class="icon"><i class="fas fa-user-tie"></i></div>
                </div>
            </div>
        </div>
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header"><h3 class="card-title">Recent Payments</h3></div>
                    <div class="card-body">
                        <table class="table table-bordered table-hover">
                            <thead class="thead-dark"><tr><th>Date</th><th>Method</th><th>Amount</th><th>Ref</th></tr></thead>
                            <tbody>
                                {% for p in payments %}
                                <tr><td>{{ p.payment_date }}</td><td>{{ p.method }}</td><td>${{ p.amount_paid }}</td><td>{{ p.reference_number|default:"-" }}</td></tr>
                                {% empty %}
                                <tr><td colspan="4">No payments recorded</td></tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>
{% endblock content %}""")

# staff_view_salary_structure.html
write_file(base_path + "staff_template/accounting/view_salary_structure.html", """{% extends 'main_app/base.html' %}
{% block page_title %}My Salary Structure{% endblock page_title %}
{% block content %}
<section class="content">
    <div class="container-fluid">
        <div class="card">
            <div class="card-header"><h3 class="card-title">Current Salary Structure</h3></div>
            <div class="card-body">
                {% if structure %}
                <ul class="list-group">
                    <li class="list-group-item"><b>Basic Salary:</b> ${{ structure.basic_salary }}</li>
                    <li class="list-group-item"><b>Allowances:</b> ${{ structure.allowances }}</li>
                    <li class="list-group-item"><b>Effective From:</b> {{ structure.effective_from }}</li>
                </ul>
                {% else %}
                <p>No salary structure assigned yet.</p>
                {% endif %}
            </div>
        </div>
    </div>
</section>
{% endblock content %}""")

# staff_view_payslips.html
write_file(base_path + "staff_template/accounting/view_payslips.html", """{% extends 'main_app/base.html' %}
{% block page_title %}My Payslips{% endblock page_title %}
{% block content %}
<section class="content">
    <div class="container-fluid">
        <div class="card">
            <div class="card-header"><h3 class="card-title">Payslip History</h3></div>
            <div class="card-body">
                <table class="table table-bordered table-hover">
                    <thead class="thead-dark"><tr><th>Month/Year</th><th>Gross</th><th>Deductions</th><th>Net</th><th>Status</th><th>Paid Date</th></tr></thead>
                    <tbody>
                        {% for p in payslips %}
                        <tr>
                            <td>{{ p.month }}/{{ p.year }}</td>
                            <td>${{ p.gross }}</td>
                            <td>${{ p.deductions }}</td>
                            <td>${{ p.net_pay }}</td>
                            <td>{% if p.status == 'draft' %}<span class="badge badge-warning">Draft</span>{% else %}<span class="badge badge-success">Paid</span>{% endif %}</td>
                            <td>{{ p.paid_date|default:"-" }}</td>
                        </tr>
                        {% empty %}
                        <tr><td colspan="6">No payslips found.</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</section>
{% endblock content %}""")

# student_view_invoices.html
write_file(base_path + "student_template/accounting/view_invoices.html", """{% extends 'main_app/base.html' %}
{% block page_title %}My Invoices{% endblock page_title %}
{% block content %}
<section class="content">
    <div class="container-fluid">
        <div class="card">
            <div class="card-header"><h3 class="card-title">My Invoices</h3></div>
            <div class="card-body">
                <table class="table table-bordered table-hover">
                    <thead class="thead-dark"><tr><th>Session</th><th>Total</th><th>Status</th><th>Due Date</th><th>Actions</th></tr></thead>
                    <tbody>
                        {% for invoice in invoices %}
                        <tr>
                            <td>{{ invoice.session }}</td>
                            <td>${{ invoice.total_amount }}</td>
                            <td>
                                {% if invoice.status == 'paid' %}<span class="badge badge-success">Paid</span>
                                {% elif invoice.status == 'partial' %}<span class="badge badge-warning">Partial</span>
                                {% elif invoice.status == 'overdue' %}<span class="badge badge-danger">Overdue</span>
                                {% else %}<span class="badge badge-secondary">Unpaid</span>{% endif %}
                            </td>
                            <td>{{ invoice.due_date }}</td>
                            <td><a href="{% url 'student_view_invoice_details' invoice.id %}" class="btn btn-sm btn-info">View Breakdown</a></td>
                        </tr>
                        {% empty %}
                        <tr><td colspan="5">No invoices found.</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</section>
{% endblock content %}""")


# student_view_invoice_details.html
write_file(base_path + "student_template/accounting/view_invoice_details.html", """{% extends 'main_app/base.html' %}
{% block page_title %}Invoice Details{% endblock page_title %}
{% block content %}
<section class="content">
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header"><h3 class="card-title">Itemized Breakdown</h3></div>
                    <div class="card-body">
                        <ul class="list-group">
                            {% for item in items %}
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                {{ item.category.name }}
                                <span>${{ item.amount }}</span>
                            </li>
                            {% endfor %}
                            <li class="list-group-item d-flex justify-content-between align-items-center bg-light">
                                <b>Total</b>
                                <b>${{ invoice.total_amount }}</b>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header"><h3 class="card-title">Payment History</h3></div>
                    <div class="card-body">
                        <table class="table table-sm table-bordered">
                            <thead><tr><th>Date</th><th>Method</th><th>Amount</th></tr></thead>
                            <tbody>
                                {% for p in payments %}
                                <tr><td>{{ p.payment_date }}</td><td>{{ p.method }}</td><td>${{ p.amount_paid }}</td></tr>
                                {% empty %}
                                <tr><td colspan="3">No payments made yet.</td></tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>
{% endblock content %}""")

