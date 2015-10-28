# -*- encoding: utf-8 -*-
##############################################################################
#
#    HR Expense Analytic Default module for OpenERP
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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


class hr_employee(orm.Model):
    _inherit = 'hr.employee'

    _columns = {
        'default_analytic_account_id': fields.many2one(
            'account.analytic.account', 'Default Analytic Account',
            domain=[('type', 'not in', ('view', 'template'))],
            help="This field will be copied on the expenses of this employee."
            ),
        }


class hr_expense_expense(orm.Model):
    _inherit = 'hr.expense.expense'

    _columns = {
        'default_analytic_account_id': fields.many2one(
            'account.analytic.account', 'Default Analytic Account',
            domain=[('type', 'not in', ('view', 'template'))]),
        }

    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        res = super(hr_expense_expense, self).onchange_employee_id(
            cr, uid, ids, employee_id, context=context)
        analytic_account_id = False
        if employee_id:
            employee = self.pool['hr.employee'].browse(
                cr, uid, employee_id, context=context)
            analytic_account_id = \
                employee.default_analytic_account_id.id or False
        res['value']['default_analytic_account_id'] = analytic_account_id
        return res
