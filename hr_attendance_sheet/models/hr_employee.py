# Copyright 2020 Pavlov Media
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class HrEmployee(models.Model):

    _inherit = "hr.employee"

    hours_to_work = fields.Float(
        string="Hours to Work",
        help="""Expected working hours based on company policy. This is used \
             on attendance sheets to calculate overtime values.""",
    )

    use_attendance_sheets = fields.Boolean(
        string="Use Attendance Sheets",
        help="""Used in the attendance sheet auto creation process. Employees \
             that have the 'Hourly' type will have attendance sheets \
             automatically created""",
    )

    attendance_admin = fields.Many2one(
        "hr.employee",
        string="Attendance Admin",
        help="""In addition to the employees manager, this person can
        administer attendances for all employees in the department. This field
        is set on the department.""",
        related="department_id.attendance_admin",
    )
