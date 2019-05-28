# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResourceCalendarAttendance(models.Model):

    _inherit = 'resource.calendar.attendance'

    rest_time = fields.Float(string='Rest Time')

    @api.onchange('rest_time')
    def _onchange_rest_time(self):
        # avoid negative or after midnight
        self.rest_time = min(self.rest_time, 23.99)
        self.rest_time = max(self.rest_time, 0.0)

    @api.constrains('hour_from', 'hour_to', 'rest_time')
    def _check_rest_time(self):
        for record in self:
            if record.hour_to - record.hour_from < record.rest_time:
                raise ValidationError(
                    _('Rest time cannot be greater than the interval time')
                )
