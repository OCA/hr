# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta


from odoo import api, models
from odoo.tools.float_utils import float_round


class ResourceCalendar(models.Model):

    _inherit = 'resource.calendar'

    def _get_work_hours(self, start, stop, meta):
        return (stop - start - timedelta(hours=sum([
            attendance.rest_time for attendance in meta
        ]))).total_seconds() / 3600

    @api.onchange('attendance_ids')
    def _onchange_hours_per_day(self):
        if self.env.context.get('use_old_onchange_hours_per_day'):
            return super()._onchange_hours_per_day()
        attendances = self.attendance_ids.filtered(
            lambda att: not att.date_from and not att.date_to
        )
        hour_count = 0.0
        for att in attendances:
            hour_count += att.hour_to - att.hour_from - att.rest_time

        if attendances:
            self.hours_per_day = float_round(
                hour_count / float(len(set(attendances.mapped('dayofweek')))),
                precision_digits=2)
