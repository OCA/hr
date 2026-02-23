# Copyright 2025 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    collective_agreement_ids = fields.Many2many(
        comodel_name="collective.agreement",
        relation="collective_agreement_partner_rel",
        column1="partner_id",
        column2="agreement_id",
        string="Collective Agreements",
        check_company=True,
    )
    collective_agreement_count = fields.Integer(
        string="Collective Agreements Count",
        compute="_compute_collective_agreement_count",
    )

    def _compute_collective_agreement_count(self):
        for partner in self:
            partner.collective_agreement_count = len(partner.collective_agreement_ids)

    def action_view_collective_agreements(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Collective Agreements",
            "res_model": "collective.agreement",
            "view_mode": "list",
            "view_id": self.env.ref(
                "hr_collective_agreement_partner.view_collective_agreement_tree_partner"
            ).id,
            "domain": [
                ("partner_ids", "in", [self.id]),
            ],
            "context": {
                "partner_id": self.id,
                "default_partner_id": self.id,
            },
            "target": "current",
        }
