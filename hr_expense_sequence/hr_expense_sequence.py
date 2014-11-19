# -*- encoding: utf-8 -*-
##############################################################################
#
#    HR Expense Sequence module for OpenERP
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
from openerp.tools.translate import _


class hr_expense_expense(orm.Model):
    _inherit = 'hr.expense.expense'
    _order = 'name desc'

    _columns = {
        # Move the description from the 'name' field to 'description' field
        # In the 'name' field, we now store the number/sequence
        'name': fields.char('Number', size=32, readonly=True),
        'description': fields.char(
            'Description', size=128, required=True, readonly=True,
            states={
                'draft': [('readonly', False)],
                'confirm': [('readonly', False)],
            }),
        }

    _defaults = {
        'name': '/',
        }

    _sql_constraints = [(
        'company_name_uniq',
        'unique(company_id, name)',
        'An expense with that number already exists in the same company !')]

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['name'] = '/'
        expense = self.browse(cr, uid, id, context=context)
        default['description'] = _("%s (copy)") % (expense.description or '')
        return super(hr_expense_expense, self).copy(
            cr, uid, id, default=default, context=context)

    def create(self, cr, uid, vals, context=None):
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool['ir.sequence'].next_by_code(
                cr, uid, 'hr.expense.expense', context=context)
        return super(hr_expense_expense, self).create(
            cr, uid, vals, context=context)
