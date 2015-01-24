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


class hr_payslip(orm.Model):
    """
    Make the employee_id field not required, because hr_payslip is inherited
    by hr_employer_contribution and employee_id makes no sence in the later
    one.

    Instead, required="1" is added on field employee_id of
    view_hr_payslip_form
    """
    _name = 'hr.payslip'
    _inherit = 'hr.payslip'
    _columns = {
        'employee_id': fields.many2one(
            'hr.employee',
            'Employee',
            required=False,
            readonly=True,
            states={'draft': [('readonly', False)]}
        ),
    }
