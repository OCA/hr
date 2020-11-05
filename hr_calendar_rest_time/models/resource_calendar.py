# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import models


class ResourceCalendar(models.Model):

    _inherit = "resource.calendar"

    def _get_work_hours_interval(self, start, stop, meta):
        return (
            stop
            - start
            - timedelta(hours=sum([attendance.rest_time for attendance in meta]))
        ).total_seconds() / 3600

    def _get_work_hours_attendance(self, attendance):
        return attendance.hour_to - attendance.hour_from - attendance.rest_time
