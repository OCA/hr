# -*- coding: utf-8 -*-

# Copyright (C) 2016 Open Net Sarl
# Copyright (C) 2018 Compassion CH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class ResCalendarAttendance(models.Model):
    _inherit = 'resource.calendar.attendance'

    due_hours = fields.Float()
