# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.resource.models.resource import HOURS_PER_DAY


class HrLeaveAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    number_of_hours = fields.Float(
        'Allocated hours',
        compute='_compute_number_of_hours',
        readonly=True,
        store=True,
        help="UX field allowing to see and modify the allocation duration,"
             "computed in hours.")

    @api.depends('number_of_days', 'employee_id')
    def _compute_number_of_hours(self):
        for allocation in self:
            allocation.number_of_hours = allocation.number_of_days * (
                allocation.employee_id.resource_calendar_id.hours_per_day
                or HOURS_PER_DAY)
