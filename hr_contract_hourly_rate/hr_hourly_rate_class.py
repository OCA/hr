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
from itertools import permutations


class hr_hourly_rate_class(orm.Model):
    _name = 'hr.hourly.rate.class'
    _description = 'Hourly rate class'
    _columns = {
        'name': fields.char(
            'Class Name',
            required=True,
        ),
        'line_ids': fields.one2many(
            'hr.hourly.rate',
            'class_id',
            'Hourly Rates'
        ),
        'contract_job_ids': fields.one2many(
            'hr.contract.job',
            'hourly_rate_class_id',
            'Contract Jobs'
        ),
    }

    def _check_overlapping_rates(self, cr, uid, ids, context=None):
        """
        Checks if a class has two rates that overlap in time.
        """
        for hourly_rate_class in self.browse(cr, uid, ids, context):

            for r1, r2 in permutations(hourly_rate_class.line_ids, 2):
                if r1.date_end and (
                        r1.date_start <= r2.date_start <= r1.date_end):
                    return False
                elif not r1.date_end and (r1.date_start <= r2.date_start):
                    return False

        return True

    _constraints = [(
        _check_overlapping_rates,
        'Error! You cannot have overlapping rates',
        ['line_ids']
    )]
