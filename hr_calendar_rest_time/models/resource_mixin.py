# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from datetime import timedelta


class ResourceMixin(models.AbstractModel):
    _inherit = 'resource.mixin'

    def _get_work_hours(self, start, stop, meta):
        return (stop - start - timedelta(hours=sum([
            attendance.rest_time for attendance in meta
        ]))).total_seconds() / 3600
