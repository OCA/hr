# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from datetime import timedelta


class ResourceMixin(models.AbstractModel):
    _inherit = 'resource.mixin'

    def _get_work_hours(self, interval):
        return (interval[1] - interval[0]) - timedelta(hours=sum([
            attendance.rest_time for attendance in interval[2]['attendances']
        ]))
