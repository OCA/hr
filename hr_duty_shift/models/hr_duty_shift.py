# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrDutyShift(models.Model):

    _name = 'hr.duty.shift'
    _description = 'Duty Shift'
    _order = 'start_date desc'

    start_date = fields.Datetime(required=True)
    end_date = fields.Datetime(required=True)
    employee_id = fields.Many2one(
        'hr.employee', required=True,
        default=lambda r: r.env.user.employee_ids[:1]
    )

    is_paid = fields.Boolean(string='Extra Paid')

    display_name = fields.Char(
        "Name",
        compute="_compute_display_name",
        readonly=True,
        store=True,
    )

    @api.depends('employee_id', 'start_date')
    def _compute_display_name(self):
        for r in self:
            r.display_name = '%s - %s' % (
                r.employee_id.name,
                fields.Datetime.from_string(
                    r.start_date
                ).strftime('%Y-%m-%d')
            )
