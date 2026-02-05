# Copyright 2025 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class CollectiveAgreement(models.Model):
    _inherit = "collective.agreement"

    def action_unassign_from_partner(self):
        self.ensure_one()
        partner_id = (
            self.env.context.get("partner_id")
            or self.env.context.get("default_partner_id")
            or self.env.context.get("active_id")
        )
        if partner_id:
            partner = self.env["res.partner"].browse(partner_id)
            partner.collective_agreement_ids -= self
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }
