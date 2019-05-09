# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.resource.models.resource import HOURS_PER_DAY


class HrLeave(models.Model):
    _inherit = "hr.leave"

    number_of_hours = fields.Float(
        'Duration (hours)',
        compute='_compute_number_of_hours',
        readonly=True,
        store=True,
        help='Number of hours of the leave request according to '
             'your working schedule.')

    @api.depends('number_of_days', 'employee_id', 'date_from', 'date_to')
    def _compute_number_of_hours(self):
        for leave in self:
            cal = leave.employee_id.resource_calendar_id
            cal = cal or self.env.user.company_id.resource_calendar_id
            hours = cal.get_work_hours_count(
                leave.date_from, leave.date_to)
            hours = hours or (leave.number_of_days * HOURS_PER_DAY)
            leave.number_of_hours = hours
