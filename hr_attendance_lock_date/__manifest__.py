# Copyright camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "HR Attendance lock date",
    "version": "11.0.1.0.0",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "author": "camptocamp, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "hr_attendance",
        "timesheet_grid",
    ],
    "data": [
        "views/employee_view.xml",
    ],
}
