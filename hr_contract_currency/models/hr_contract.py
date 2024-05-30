# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrContract(models.Model):
    _inherit = "hr.contract"

    currency_id = fields.Many2one(
        "res.currency",
        related=False,
        readonly=False,
        required=True,
        default=lambda self: self._get_default_currency_id(),
        tracking=True,
    )

    def _get_default_currency_id(self):
        return self.company_id.currency_id or self.env.company.currency_id

    @api.model
    def create(self, vals):
        if vals.get("company_id") and not vals.get("currency_id"):
            company = self.env["res.company"].browse(vals.get("company_id"))
            vals["currency_id"] = company.currency_id.id
        return super().create(vals)
