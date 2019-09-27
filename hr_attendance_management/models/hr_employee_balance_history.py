# -*- coding: utf-8 -*-

# Copyright (C) 2018 Compassion CH
# Author: Quentin Gigon <gigon.quentin@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import datetime
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class HrEmployeeBalanceHistory(models.Model):
    _name = "hr.employee.balance.history"

    date = fields.Date(string='Date of balance computation', readonly=True)
    balance = fields.Float(string='Hours balance at the date of computation', readonly=True)
    previous_balance = fields.Float(string='Balance of previous period', readonly=True)
    lost = fields.Float(string='Hours lost at the date of computation', readonly=True)
    employee_id = fields.Many2one("hr.employee", string='Employee', required=True, readonly=True)
    continuous_cap = fields.Boolean(string='Continuous cap for this period')

    @api.multi
    def write(self, vals):
        res = super(HrEmployeeBalanceHistory, self).write(vals)
        for entry in self:
            if 'continuous_cap' in vals:
                previous_history_entry = self.env['hr.employee.balance.history'].search([
                    ('employee_id', '=', entry.employee_id.id),
                    ('date', '<', entry.date)
                ], order='date desc', limit=1)

                start_date = None
                end_date = entry.date
                balance = None

                if previous_history_entry:
                    start_date = previous_history_entry.date
                    balance = previous_history_entry.balance
                else:
                    start_date = datetime.date.today().replace(year=2018, month=1, day=1)
                    balance = entry.employee_id.initial_balance

                entry.employee_id.update_past_periods(start_date,
                                                      end_date,
                                                      balance)
        return res
