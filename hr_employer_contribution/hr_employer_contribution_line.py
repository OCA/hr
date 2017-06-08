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
import openerp.addons.decimal_precision as dp


class hr_contribution_line(orm.Model):
    '''
    Employer contribution contribution line
    '''
    _name = 'hr.employer.contribution.line'
    _inherit = 'hr.salary.rule'
    _description = 'Employer Contribution Line'
    _order = 'sequence'

    def _calculate_total(self, cr, uid, ids, name, args, context):
        if not ids:
            return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = float(line.quantity) * line.amount * line.rate / 100
        return res

    _columns = {
        'contribution_id': fields.many2one(
            'hr.employer.contribution',
            'Pay Slip',
            required=True,
            ondelete='cascade'
        ),
        'salary_rule_id': fields.many2one(
            'hr.salary.rule', 'Rule',
            required=True
        ),
        'rate': fields.float(
            'Rate (%)',
            digits_compute=dp.get_precision('Payroll Rate')
        ),
        'amount': fields.float(
            'Amount',
            digits_compute=dp.get_precision('Payroll')
        ),
        'quantity': fields.float(
            'Quantity',
            digits_compute=dp.get_precision('Payroll')
        ),
        'total': fields.function(
            _calculate_total,
            method=True,
            type='float',
            string='Total',
            digits_compute=dp.get_precision('Payroll'),
            store=True
        ),
    }
    _defaults = {
        'quantity': 1.0,
        'rate': 100.0,
    }
