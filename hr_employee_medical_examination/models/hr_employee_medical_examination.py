# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployeeMedicalExamination(models.Model):

    _name = 'hr.employee.medical.examination'
    _description = 'Hr Employee Medical Examination'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        required=True,
        track_visibility='onchange',
    )

    state = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ], default='pending',
        track_visibility='onchange',
    )

    date = fields.Date(
        string='Examination Date',
        track_visibility='onchange',
    )
    result = fields.Selection(
        selection=[
            ('failed', 'Failed'),
            ('passed', 'Passed'),
        ],
        track_visibility='onchange',
    )

    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True,
        track_visibility='onchange',
    )
