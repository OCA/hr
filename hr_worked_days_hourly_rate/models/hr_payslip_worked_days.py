# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, fields, models


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    hourly_rate = fields.Float(
        'Hourly Rate',
        default=0,
        help="The employee's standard hourly rate for one hour of work."
             "Example, 25 Euros per hour.")
    rate = fields.Float(
        'Rate (%)',
        default=100,
        help="The rate by which to multiply the standard hourly rate."
             "Example, an overtime hour could be paid the standard rate"
             "multiplied by 150%.")

    # When a worked day has a number of hours and an hourly rate,
    # it is necessary to have a date interval,
    # because hourly rates are likely to change over the time.
    date_from = fields.Date('Date From', default=fields.Date.context_today)
    date_to = fields.Date('Date To', default=fields.Date.context_today)
    total = fields.Float(string='Total', compute='_compute_total')

    @api.one
    @api.depends('number_of_hours', 'hourly_rate', 'rate')
    def _compute_total(self):
        self.total = self.number_of_hours * self.hourly_rate * self.rate / 100
