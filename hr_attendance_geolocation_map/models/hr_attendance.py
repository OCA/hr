# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    def get_location(self):
        return {
            'check_in_latitude': self.check_in_latitude,
            'check_in_longitude': self.check_in_longitude,
            'check_out_latitude': self.check_out_latitude,
            'check_out_longitude': self.check_out_longitude,

        }
