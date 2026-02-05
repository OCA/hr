# Copyright 2025 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CollectiveAgreementAssignWizard(models.TransientModel):
    _name = "collective.agreement.assign.wizard"
    _description = "Assign Collective Agreements to Partner"

    partner_id = fields.Many2one(
        "res.partner",
        required=True,
        readonly=True,
    )

    collective_agreement_ids = fields.Many2many(
        "collective.agreement",
        string="Available Collective Agreements",
    )

    def action_assign(self):
        self.ensure_one()
        self.partner_id.collective_agreement_ids |= self.collective_agreement_ids
