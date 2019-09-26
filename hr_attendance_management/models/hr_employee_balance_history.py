# -*- coding: utf-8 -*-

# Copyright (C) 2018 Compassion CH
# Author: Quentin Gigon <gigon.quentin@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class HrEmployeeBalanceHistory(models.Model):
    _name = "hr.employee.balance.history"

    date = fields.Date(string='Date of balance computation')
    balance = fields.Float(string='Hours balance at the date of computation')
    previous_balance = fields.Float(string='Balance of previous period')
    lost = fields.Float(string='Hours lost at the date of computation')
    employee_id = fields.Many2one("hr.employee", string='Employee', required=True)
    continuous_cap = fields.Boolean(string='Continuous cap for this period')
