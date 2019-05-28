# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResourceCalendarAttendance(models.Model):

    _inherit = 'resource.calendar.attendance'

    rest_time = fields.Float(string='Rest Time')
