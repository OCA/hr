# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrAttendance(models.Model):
    _name = 'hr.attendance'
    _inherit = ['hr.attendance', 'mail.thread']

    employee_id = fields.Many2one(
        track_visibility='onchange'
    )
    check_in = fields.Datetime(
        track_visibility='onchange'
    )
    check_out = fields.Datetime(
        track_visibility='onchange'
    )
