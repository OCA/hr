# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    expense_analytic_id = fields.Many2one(
        'account.analytic.account',
        string="Default Analytic Account for Expenses",
        related='company_id.default_expense_analytic_id',
        readonly=False
    )
