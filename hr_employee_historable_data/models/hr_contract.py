# Copyright 2021 Iryna Vyshnevska (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.contract"

    wage_ids = fields.One2many(
        string="Wage history",
        comodel_name="hr.contract.wage",
        inverse_name="contract_id",
    )
    wage = fields.Monetary(compute="_compute_current_wage", store=True)

    @api.depends("wage_ids.date_start", "wage_ids.date_end", "wage_ids.wage")
    def _compute_current_wage(self):
        for rec in self:
            contract = rec.mapped("wage_ids").filtered(
                lambda c: c.date_start <= fields.Date.today()
                and c.date_end >= fields.Date.today()
            )
            if contract:
                rec.wage = contract[0].wage
            else:
                rec.wage = 0.0
