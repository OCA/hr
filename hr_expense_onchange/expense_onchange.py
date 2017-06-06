# -*- encoding: utf-8 -*-
##############################################################################
#
#    HR Expense Onchange module for OpenERP
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

from openerp.osv import orm


class hr_expense_line(orm.Model):
    _inherit = 'hr.expense.line'

    def common_onchange_unit_amount_quantity(
            self, cr, uid, ids, unit_amount, unit_quantity, product_id,
            employee_id, context=None):
        res = {'value': {}}
        res['value']['total_amount'] = unit_amount * unit_quantity
        return res

    def onchange_unit_amount(
            self, cr, uid, ids, unit_amount, unit_quantity,
            product_id, employee_id, context=None):
        res = self.common_onchange_unit_amount_quantity(
            cr, uid, ids, unit_amount, unit_quantity, product_id,
            employee_id, context=context)
        return res

    def onchange_unit_quantity(
            self, cr, uid, ids, unit_amount, unit_quantity,
            product_id, employee_id, context=None):
        res = self.common_onchange_unit_amount_quantity(
            cr, uid, ids, unit_amount, unit_quantity, product_id,
            employee_id, context=context)
        return res
