# -*- coding: utf-8 -*-

# Copyright (C) 2016 Open Net Sarl
# Copyright (C) 2018 Compassion CH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ResCalendarAttendance(models.Model):
    _inherit = 'resource.calendar.attendance'

    due_hours = fields.Float(compute='_compute_due_hours', readonly=True)

    @api.multi
    @api.depends('hour_from', 'hour_to')
    def _compute_due_hours(self):
        for record in self:
            record.due_hours = record.hour_to - record.hour_from
