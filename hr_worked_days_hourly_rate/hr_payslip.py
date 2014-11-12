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

from openerp.osv import orm


class hr_payslip(orm.Model):
    _name = 'hr.payslip'
    _inherit = 'hr.payslip'

    def sum_hourly_rates(
        self, cr, uid, ids,
        payslip,
        context=None,
    ):
        """
        This function is intended to be called by salary rules.

        payslip: a Payslip Browsable Object which is different from a
        browse record

        Returns the gross salary based on worked hours
        """
        res = 0

        # Unlike browse records, BrowsableObjects return 0
        # for empty one2many fields instead of []
        # so we need the if statement
        if payslip.worked_days_line_ids:
            for wd in payslip.worked_days_line_ids:
                if wd.number_of_hours:
                    res += wd.number_of_hours * wd.hourly_rate
        return res
