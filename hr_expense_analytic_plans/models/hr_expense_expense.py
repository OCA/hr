# -*- coding: utf-8 -*-
##############################################################################
#
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
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
from openerp import models, api


class HrExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

    @api.model
    def move_line_get_item(self, line):
        result = super(HrExpenseExpense, self).move_line_get_item(line)
        if line.analytics_id:
            result['account_analytic_id'] = False
            result['analytics_id'] = line.analytics_id.id
        return result

    @api.model
    def line_get_convert(self, x, part, date):
        result = super(HrExpenseExpense, self).line_get_convert(x, part, date)
        result['analytics_id'] = x.get('analytics_id', False)
        return result
