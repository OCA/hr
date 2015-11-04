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
from openerp import models, fields, api


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    @api.multi
    @api.depends('number_of_hours', 'hourly_rate', 'rate')
    def _get_total(self):
        for wd in self:
            wd.total = wd.number_of_hours * wd.hourly_rate * wd.rate / 100

    hourly_rate = fields.Float(
        string='Hourly Rate',
        default=0,
        help="The employee's standard hourly rate for one hour of work. \
        Example, 25 Euros per hour.")
    rate = fields.Float(
        string='Rate (%)',
        default=100,
        help="The rate by which to multiply the standard hourly rate. \
        Example, an overtime hour could be paid the standard rate multiplied \
        by 150%.")

    # When a worked day has a number of hours and an hourly rate,
    # it is necessary to have a date interval,
    # because hourly rates are likely to change over the time.
    date_from = fields.Date(string='Date From', default=fields.Date.today())
    date_to = fields.Date(string='Date To', default=fields.Date.today())
    total = fields.Float(string="Total", compute=_get_total, method=True)
