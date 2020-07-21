# Copyright 2020 Pavlov Media
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class HrDepartment(models.Model):
    _inherit = "hr.department"

    attendance_admin = fields.Many2one(
        "hr.employee",
        string="Attendance Admin",
        help="""In addition to the employees manager, this person can
        administer attendances for all employees in the department.""",
    )
