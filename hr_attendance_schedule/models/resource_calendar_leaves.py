# -*- coding: utf-8 -*-
from odoo import models
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT


class ResourceCalendarLeaves(models.Model):
    _inherit = 'resource.calendar.leaves'

    def matches(self, datetime):
        date_from = datetime.strptime(self.date_from, DEFAULT_SERVER_DATETIME_FORMAT)
        date_to = datetime.strptime(self.date_to, DEFAULT_SERVER_DATETIME_FORMAT)
        return date_from <= datetime <= date_to
