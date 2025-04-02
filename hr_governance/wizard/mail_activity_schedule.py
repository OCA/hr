# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MailActivitySchedule(models.TransientModel):
    _inherit = "mail.activity.schedule"

    @api.depends("activity_type_id")
    def _compute_activity_user_id(self):
        res = super()._compute_activity_user_id()
        reorganization_proposal = self.env.ref(
            "hr_governance.reorganization_proposal", raise_if_not_found=False
        )
        if not reorganization_proposal:
            return res
        for scheduler in self.filtered(
            lambda rec: rec.activity_type_id == reorganization_proposal
        ):
            governance_obj = self.env["governance.circle"]
            active_id = self.env.context.get("active_id")
            record = governance_obj.browse(active_id)
            user_ids = record._get_steering_role_user_ids()
            scheduler.activity_user_id = user_ids[0] if user_ids else False

    @api.depends("res_model")
    def _compute_activity_type_id(self):
        res = super()._compute_activity_type_id()
        reorganization_proposal = self.env.ref(
            "hr_governance.reorganization_proposal", raise_if_not_found=False
        )
        if not reorganization_proposal:
            return res
        for scheduler in self.filtered(
            lambda rec: rec.res_model == "governance.circle"
        ):
            scheduler.activity_type_id = reorganization_proposal.id
