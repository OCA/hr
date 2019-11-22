# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import ValidationError
from math import sin, cos, sqrt, atan2, radians


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _get_distance(self, a_lat, a_lng, e_lat, e_lng):
        # approximate radius of earth in km
        R = 6373.0

        lat1 = radians(a_lat)
        lon1 = radians(a_lng)
        lat2 = radians(e_lat)
        lon2 = radians(e_lng)

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return distance

    @api.multi
    def attendance_action_change(self):
        found_allowed = False
        allowed_locations = self.env['hr.attendance.location'].search([
            ('company_id', '=', self.company_id.id), ('active', '=', True)
        ])
        location = self.env.context.get('attendance_location', False)
        for allowed_location in allowed_locations:
            if allowed_location.allowed_radius > 0.0:
                distance = self._get_distance(
                    location[0], location[1],
                    allowed_location.latitude, allowed_location.longitude)
                if distance < allowed_location.allowed_radius:
                    found_allowed = True
        if found_allowed or len(allowed_location) == 0:
            return super().attendance_action_change()
        else:
            raise ValidationError(
                _("You must be within the allowed range to register your"
                  " attendance")
            )
