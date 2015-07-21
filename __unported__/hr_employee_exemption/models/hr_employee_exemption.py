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

from openerp.osv import orm, fields


class HrEmployeeExemption(orm.Model):
    _name = 'hr.employee.exemption'
    _description = 'Employee Income Tax Exemption'

    _columns = {
        'employee_id': fields.many2one(
            'hr.employee',
            'Employee',
            required=True,
            ondelete='cascade',
        ),
        'exemption_id': fields.many2one(
            'hr.income.tax.exemption',
            'Exemption',
            required=True,
        ),
        'date_from': fields.date('Date From', required=True),
        'date_to': fields.date('Date To'),
    }
