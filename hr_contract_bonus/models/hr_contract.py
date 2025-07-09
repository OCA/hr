# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Contract(models.Model):
    _inherit = "hr.contract"

    bonus_ids = fields.Many2many(
        comodel_name="hr.contract.bonus",
        string="Bonuses",
        help="List of bonuses that can be applied to the employee's contract.",
    )
    total_annual_wage_without_bonus = fields.Float(
        string="Total annual wage without bonus",
        compute="_compute_total_annual_wage_without_bonus",
        help="Total wage excluding the bonus applied to the employee's contract.",
    )
    total_annual_wage_with_bonus = fields.Float(
        string="Total annual wage with bonus",
        compute="_compute_total_annual_wage_with_bonus",
        help="Total wage including the bonus applied to the employee's contract.",
    )

    @api.depends("wage")
    def _compute_total_annual_wage_without_bonus(self):
        for contract in self:
            contract.total_annual_wage_without_bonus = round(contract.wage * 12, 2)

    @api.depends("wage", "bonus_ids.amount", "bonus_ids.type", "bonus_ids.frequency")
    def _compute_total_annual_wage_with_bonus(self):
        for contract in self:
            contract.total_annual_wage_with_bonus = contract.wage * 12
            if contract.bonus_ids:
                for bonus in contract.bonus_ids:
                    if bonus.type == "fixed":
                        if bonus.frequency == "monthly":
                            contract.total_annual_wage_with_bonus += bonus.amount * 12

                        else:
                            contract.total_annual_wage_with_bonus += bonus.amount
                    else:
                        if bonus.frequency == "monthly":
                            contract.total_annual_wage_with_bonus += (
                                contract.wage * (bonus.amount / 100)
                            ) * 12
                        else:
                            contract.total_annual_wage_with_bonus += (
                                contract.wage * 12
                            ) * (bonus.amount / 100)

            contract.total_annual_wage_with_bonus = round(
                contract.total_annual_wage_with_bonus, 2
            )
