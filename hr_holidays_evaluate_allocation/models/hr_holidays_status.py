# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2015 Salton Massally (<smassally@idtlabs.sl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from datetime import date

from openerp import models, fields, api


class HrHolidaysStatus(models.Model):
    _inherit = 'hr.holidays.status'

    ruleset_id = fields.Many2one(
        'hr.holidays.evaluation.ruleset',
        'Allocation Evaluation Ruleset',
        help="Allocation Evaluation Ruleset to be used by this holiday type.",
    )

    @api.multi
    def get_days(self, employee_id, dt=None):
        dt = dt or date.today()
        result = dict(
            (id, dict(max_leaves=0, leaves_taken=0, remaining_leaves=0,
                      virtual_remaining_leaves=0))
            for id in self.ids
        )

        employee = self.env['hr.employee'].browse(employee_id)
        holiday_obj = self.env['hr.holidays']
        for status in self:
            ruleset = status.ruleset_id
            if status.limit:
                continue
            if ruleset.period == 'anniversary' and not employee.date_start:
                # how can we fail gracefully yet let user know why
                continue
            result[status.id]['max_leaves'] = ruleset.evaluate_allocation(
                employee, dt=dt)
            result[status.id]['leaves_taken'] = ruleset.evaluate_withdrawals(
                status, employee, dt=dt)
            result[status.id]['remaining_leaves'] = (
                result[status.id]['max_leaves']
                + result[status.id]['leaves_taken']
            )

            # let gather ones waiting validation in this period
            period_start, period_end = ruleset.holidays_period(employee, dt)
            pending_validation = holiday_obj.search(
                [
                    ('employee_id', '=', employee.id),
                    ('state', 'in', ('validate1', 'confirm')),
                    ('holiday_status_id', '=', status.id),
                    ('date_from', '>=', str(period_start)),
                    ('date_from', '<=', str(period_end)),
                    ('type', '=', 'remove'),
                    ('holiday_type', '=', 'employee')
                ]
            ).mapped('number_of_days')
            result[status.id]['virtual_remaining_leaves'] = (
                result[status.id]['remaining_leaves']
                + sum(pending_validation)
            )
        return result
