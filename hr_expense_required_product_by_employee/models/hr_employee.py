# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    required_expense_product = fields.Boolean(
        string='Required Expense Product',
        default=False)
