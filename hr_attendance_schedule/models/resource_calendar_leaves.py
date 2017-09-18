# -*- coding: utf-8 -*-
from odoo import fields, models


class ResourceCalendarLeaves(models.Model):
    _inherit = 'resource.calendar.leaves'

    def matches(self, datetime):
        date_from = fields.Datetime.from_string(self.date_from)
        date_to = fields.Datetime.from_string(self.date_to)
        return date_from <= datetime <= date_to
