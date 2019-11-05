# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class RecomputeTheoreticalAttendance(models.TransientModel):
    _name = 'recompute.theoretical.attendance'
    _description = 'Recompute Employees Attendances'

    employee_ids = fields.Many2many(
        comodel_name='hr.employee',
        required=True,
        string='Employees',
        help='Recompute these employees attendances',
    )
    date_from = fields.Datetime(
        string='From',
        required=True,
        help='Recompute attendances from this date',
    )
    date_to = fields.Datetime(
        string='To',
        required=True,
        help='Recompute attendances up to this date',
    )

    @api.multi
    def action_recompute(self):
        self.ensure_one()
        attendances = self.env['hr.attendance'].search([
            ('employee_id', 'in', self.employee_ids.ids),
            ('check_in', '>=', self.date_from),
            ('check_out', '<=', self.date_to),
        ])
        attendances._compute_theoretical_hours()
        return {'type': 'ir.actions.act_window_close'}
