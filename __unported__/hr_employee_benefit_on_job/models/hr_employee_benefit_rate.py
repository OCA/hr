# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Savoir-faire Linux. All Rights Reserved.
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

from openerp.osv import orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _
from datetime import datetime
strptime = datetime.strptime


class HrEmployeeBenefitRate(orm.Model):
    _inherit = 'hr.employee.benefit.rate'

    def get_all_amount_types(self, cr, uid, context=None):
        res = super(HrEmployeeBenefitRate, self).get_all_amount_types(
            cr, uid, context=context)

        res.append(('per_hour', _('Per Worked Hour')))

        return res

    def compute_amounts_per_hour(
        self, cr, uid, ids, wd, context=None
    ):
        """
        Compute the amounts of benefit that are calculated over worked hours.
        """
        wd_from = strptime(wd.date_from, DEFAULT_SERVER_DATE_FORMAT)
        wd_to = strptime(wd.date_to, DEFAULT_SERVER_DATE_FORMAT)
        duration = (wd_to - wd_from).days + 1

        for rate in self.browse(cr, uid, ids, context=context):

            rate_lines = [
                line for line in rate.line_ids
                if (
                    not line.date_end or wd.date_from <= line.date_end
                ) and line.date_start <= wd.date_to
            ]

            for line in rate_lines:
                # Case where the benefit begins after the worked days
                date_start = strptime(
                    line.date_start, DEFAULT_SERVER_DATE_FORMAT)
                start_offset = max((date_start - wd_from).days, 0)

                # Case where the benefit ends before the worked days
                date_end = line.date_end and strptime(
                    line.date_end, DEFAULT_SERVER_DATE_FORMAT) or False

                end_offset = date_end and max((wd_to - date_end).days, 0) or 0

                ratio = 1 - float(start_offset + end_offset) / duration

                self.pool['hr.payslip.benefit.line'].create(
                    cr, uid, {
                        'payslip_id': wd.payslip_id.id,
                        'employer_amount': ratio * line.employer_amount *
                        wd.number_of_hours,
                        'employee_amount': ratio * line.employee_amount *
                        wd.number_of_hours,
                        'category_id': line.category_id.id,
                        'source': 'contract',
                    }, context=context)
