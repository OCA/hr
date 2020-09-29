# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    default_expense_analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Default Analytic Account for Expenses')
