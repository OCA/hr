# -*- coding: utf-8 -*-
# Copyright (C) 2018 Compassion CH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class HrHolidaysStatus(models.Model):
    _inherit = 'hr.holidays.status'

    keep_due_hours = fields.Boolean(oldname='remove_from_due_hours')
