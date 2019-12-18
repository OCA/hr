# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# Copyright 2018 Brainbean Apps
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    @api.multi
    def _leave_intervals(self, start_dt, end_dt, resource=None, domain=None):
        res = super()._leave_intervals(
            start_dt=start_dt,
            end_dt=end_dt,
            resource=resource,
            domain=domain,
        )
        if not self.env.context.get('exclude_public_holidays'):
            intervals = []
            for start, end, record in res:
                if not record.is_public_holidays:
                    intervals |= res
            return intervals
        return res


class ResourceCalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"

    def compute_is_public(self):
        return self.env.context.get('is_public_holidays', False)

    is_public_holidays = fields.Boolean(
        default=lambda r: r.compute_is_public()
    )
