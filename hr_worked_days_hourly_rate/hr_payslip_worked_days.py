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

from openerp.osv import fields, orm
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class hr_payslip_worked_days(orm.Model):
    _inherit = 'hr.payslip.worked_days'

    def _get_total(
        self, cr, uid, ids, field_name, arg=None, context=None
    ):
        res = {}
        for wd in self.browse(cr, uid, ids, context=context):
            res[wd.id] = wd.number_of_hours \
                * wd.hourly_rate * wd.rate / 100
        return res

    _columns = {
        'hourly_rate': fields.float(
            'Hourly Rate',
            help="""\
The employee's standard hourly rate for one hour of work.
Example, 25 Euros per hour."""
        ),
        'rate': fields.float(
            'Rate (%)',
            help="""\
The rate by which to multiply the standard hourly rate.
Example, an overtime hour could be paid the standard rate multiplied by 150%.
"""
        ),

        # When a worked day has a number of hours and an hourly rate,
        # it is necessary to have a date interval,
        # because hourly rates are likely to change over the time.
        'date_from': fields.date('Date From'),
        'date_to': fields.date('Date To'),
        'total': fields.function(
            _get_total,
            method=True,
            type="float",
            string="Total",
        ),
    }
    _defaults = {
        'hourly_rate': 0,
        'rate': 100,
        'date_from': lambda *a: datetime.strftime(
            datetime.now(),
            DEFAULT_SERVER_DATE_FORMAT
        ),
        'date_to': lambda *a: datetime.strftime(
            datetime.now(),
            DEFAULT_SERVER_DATE_FORMAT
        ),
    }
