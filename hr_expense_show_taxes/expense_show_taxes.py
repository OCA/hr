# -*- encoding: utf-8 -*-
##############################################################################
#
#    HR Expense Show Taxes module for OpenERP
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
import openerp.addons.decimal_precision as dp


class hr_expense_expense(orm.Model):
    _inherit = 'hr.expense.expense'

    def _compute_amounts(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for expense in self.browse(cr, uid, ids, context=context):
            total = 0.0
            tax = 0.0
            for line in expense.line_ids:
                total += line.unit_amount * line.unit_quantity
                tax += line.amount_tax
            res[expense.id] = {
                'amount': total,
                'amount_tax': tax,
                'amount_untaxed': total - tax,
                }
        return res

    def _get_expenses_from_lines(self, cr, uid, ids, context=None):
        return self.pool['hr.expense.expense'].search(
            cr, uid, [('line_ids', 'in', ids)], context=context)

    _columns = {
        # Inherit the native amount field to store it
        'amount': fields.function(
            _compute_amounts, string='Total Amount', multi='amountexp',
            type='float', digits_compute=dp.get_precision('Account'),
            store={
                'hr.expense.line': (
                    _get_expenses_from_lines, [
                        'expense_id', 'unit_amount', 'unit_quantity',
                        ], 20),
                }),
        'amount_untaxed': fields.function(
            _compute_amounts, multi='amountexp',
            type='float', digits_compute=dp.get_precision('Account'),
            string='Total Untaxed', store={
                'hr.expense.expense': (
                    lambda self, cr, uid, ids, c={}: ids,
                    ['employee_id'], 10),
                'hr.expense.line': (
                    _get_expenses_from_lines, [
                        'expense_id', 'product_id',
                        'unit_amount', 'unit_quantity',
                        ], 20),
                }),
        'amount_tax': fields.function(
            _compute_amounts, multi='amountexp',
            type='float', digits_compute=dp.get_precision('Account'),
            string='Total Tax', store={
                'hr.expense.expense': (
                    lambda self, cr, uid, ids, c={}: ids,
                    ['employee_id'], 10),
                'hr.expense.line': (
                    _get_expenses_from_lines, [
                        'expense_id', 'product_id',
                        'unit_amount', 'unit_quantity',
                        ], 20),
                }),
        }

    def move_line_get(self, cr, uid, expense_id, context=None):
        '''Inherit the native function to disable the use of Default Taxes
        of the Expense Account. So this code is a copy-paste of the official
        hr_expense module ; it just commented out the lines that use the
        Default Taxes of the account (and made it PEP8 for OCA).
        This method is Copyright OpenERP S.A.
        '''
        res = []
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        if context is None:
            context = {}
        exp = self.browse(cr, uid, expense_id, context=context)
        company_currency = exp.company_id.currency_id.id

        for line in exp.line_ids:
            mres = self.move_line_get_item(cr, uid, line, context)
            if not mres:
                continue
            res.append(mres)
            current_product_line_pos = len(res) - 1
            tax_code_found = False

            # Calculate tax according to default tax on product
            taxes = []
            # Taken from product_id_onchange in account.invoice
            if line.product_id:
                # fposition_id = False
                # fpos_obj = self.pool.get('account.fiscal.position')
                # fpos = fposition_id and fpos_obj.browse(
                #    cr, uid, fposition_id, context=context) or False
                product = line.product_id
                taxes = product.supplier_taxes_id
                # If taxes are not related to the product, maybe they are in
                # the account
                # Alexis de Lattre : NO, I do NOT want this behaviour
                # That's why the lines of code below are commented
                # if not taxes:
                #    a = product.property_account_expense.id
                # Why is not there a check here?
                #    if not a:
                #        a = product.categ_id.property_account_expense_categ.id
                #    a = fpos_obj.map_account(cr, uid, fpos, a)
                #    taxes = a and self.pool.get('account.account').browse(
                #        cr, uid, a, context=context).tax_ids or False
                # tax_id = fpos_obj.map_tax(cr, uid, fpos, taxes)
            if not taxes:
                continue
            # Calculating tax on the line and creating move?
            for tax in tax_obj.compute_all(
                    cr, uid, taxes,
                    line.unit_amount,
                    line.unit_quantity, line.product_id,
                    exp.user_id.partner_id)['taxes']:
                tax_code_id = tax['base_code_id']
                tax_amount = line.total_amount * tax['base_sign']
                if tax_code_found:
                    if not tax_code_id:
                        continue
                    res.append(self.move_line_get_item(cr, uid, line, context))
                    res[-1]['price'] = 0.0
                    res[-1]['account_analytic_id'] = False
                elif not tax_code_id:
                    continue
                tax_code_found = True
                res[-1]['tax_code_id'] = tax_code_id
                res[-1]['tax_amount'] = cur_obj.compute(
                    cr, uid, exp.currency_id.id, company_currency,
                    tax_amount, context={'date': exp.date_confirm})
                ##
                is_price_include = tax_obj.read(
                    cr, uid, tax['id'], ['price_include'],
                    context)['price_include']
                if is_price_include:
                    ## We need to deduce the price for the tax
                    res[current_product_line_pos]['price'] = (
                        res[current_product_line_pos]['price']
                        - (-(tax['amount'] * tax['base_sign'] or 0.0)))
                # Will create the tax here as we don't have the access
                if (
                        (tax['amount'] * tax['base_sign'] or 0.0)
                        or tax['tax_code_id'] is not False):
                    assoc_tax = {
                        'type': 'tax',
                        'name': tax['name'],
                        'price_unit': tax['price_unit'],
                        'quantity': 1,
                        'price': -(tax['amount'] * tax['base_sign'] or 0.0),
                        'account_id':
                        tax['account_collected_id'] or mres['account_id'],
                        'tax_code_id': tax['tax_code_id'],
                        'tax_amount': tax['amount'] * tax['base_sign'],
                        }
                    res.append(assoc_tax)
        return res


class hr_expense_line(orm.Model):
    _inherit = 'hr.expense.line'

    def _compute_tax_untaxed(
            self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            taxes = \
                line.product_id and line.product_id.supplier_taxes_id or False
            total = line.unit_amount * line.unit_quantity
            if taxes:
                computed_tax = self.pool['account.tax'].compute_all(
                    cr, uid, taxes, line.unit_amount,
                    line.unit_quantity, line.product_id,
                    line.expense_id.employee_id
                    and line.expense_id.employee_id.user_id.partner_id
                    or False)
                res[line.id] = {
                    'amount_untaxed': computed_tax['total'],
                    'amount_tax': total - computed_tax['total'],
                }
            else:
                res[line.id] = {
                    'amount_untaxed': total,
                    'amount_tax': 0.0,
                    }
        return res

    def _get_expense_lines_from_expenses(self, cr, uid, ids, context=None):
        return self.pool['hr.expense.line'].search(
            cr, uid, [('expense_id', 'in', ids)], context=context)

    _columns = {
        'amount_untaxed': fields.function(
            _compute_tax_untaxed, type='float',
            digits_compute=dp.get_precision('Account'),
            string='Untaxed', multi='amountexpline', store={
                'hr.expense.line': (
                    lambda self, cr, uid, ids, c={}: ids,
                    ['unit_amount', 'unit_quantity', 'product_id'], 10),
                'hr.expense.expense': (
                    _get_expense_lines_from_expenses, ['employee_id'], 20),
            }),
        'amount_tax': fields.function(
            _compute_tax_untaxed, type='float',
            digits_compute=dp.get_precision('Account'),
            string='Tax', multi='amountexpline', store={
                'hr.expense.line': (
                    lambda self, cr, uid, ids, c={}: ids,
                    ['unit_amount', 'unit_quantity', 'product_id'], 10),
                'hr.expense.expense': (
                    _get_expense_lines_from_expenses, ['employee_id'], 20),
            }),
        }

    def common_onchange_unit_amount_quantity(
            self, cr, uid, ids, unit_amount, unit_quantity,
            product_id, employee_id, context=None):
        res = super(hr_expense_line, self).\
            common_onchange_unit_amount_quantity(
                cr, uid, ids, unit_amount, unit_quantity, product_id,
                employee_id, context=context)
        total = unit_amount * unit_quantity
        if unit_amount and unit_quantity and product_id:
            product = self.pool['product.product'].browse(
                cr, uid, product_id, context=context)
            taxes = product.supplier_taxes_id or False
            partner = False
            if employee_id:
                employee = self.pool['hr.employee'].browse(
                    cr, uid, employee_id, context=context)
                partner = \
                    employee.user_id and employee.user_id.partner_id or False
            if taxes:
                computed_tax = self.pool['account.tax'].compute_all(
                    cr, uid, taxes, unit_amount,
                    unit_quantity, product_id, partner)
                res['value'].update({
                    'amount_untaxed': computed_tax['total'],
                    'amount_tax': total - computed_tax['total'],
                    })
        else:
            res['value'].update({
                'amount_untaxed': total,
                'amount_tax': 0.0,
                })
        return res

    def _check_product_exp_line(self, cr, uid, ids):
        for line in self.browse(cr, uid, ids):
            if line.product_id and line.product_id.supplier_taxes_id:
                for tax in line.product_id.supplier_taxes_id:
                    if not tax.price_include:
                        raise orm.except_orm(
                            _('Error:'),
                            _("The product '%s' has a Supplier Tax '%s' (%s) "
                                "which is not 'Tax Included'. You should "
                                "replace this tax by it's equivalent with "
                                "'Tax Included'.")
                            % (
                                line.product_id.name,
                                tax.name,
                                tax.description))
        return True

    _constraints = [(
        _check_product_exp_line,
        'Wrong Supplier Taxes on Product',
        ['product_id']
        )]


class product_product(orm.Model):
    _inherit = 'product.product'

    def _check_expense_supplier_tax(self, cr, uid, ids):
        for product in self.browse(cr, uid, ids):
            if product.hr_expense_ok and product.supplier_taxes_id:
                for tax in product.supplier_taxes_id:
                    if not tax.price_include:
                        raise orm.except_orm(
                            _('Error:'),
                            _("The product '%s' is 'Can be Expensed', but "
                                "it has a Supplier Tax '%s' (%s) which is "
                                "not 'Tax Included'. You should replace this "
                                "tax by it's equivalent with 'Tax Included'.")
                            % (product.name, tax.name, tax.description))
        return True

    _constraints = [(
        _check_expense_supplier_tax, "Error msg in raise",
        ['supplier_taxes_id', 'hr_expense_ok']
        )]
