# Copyright 2017 Odoo S.A.
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models


class HrAttendanceReason(models.Model):
    _name = "hr.attendance.reason"
    _description = "Attendance Reason"

    _sql_constraints = [
        ('unique_code', 'UNIQUE(code)', 'Code must be unique')
    ]

    name = fields.Char(
        String='Reason',
        help='Specifies the reason leaving soon or arriving late',
        required=True, index=True)
    code = fields.Char('Reason Code')
    action_type = fields.Selection(
        [('sign_in', 'Sign in'),
         ('sign_out', 'Sign out')],
        string="Action Type", help="Leave empty if it is independent")
