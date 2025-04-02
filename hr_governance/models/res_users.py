# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command, fields, models


class Users(models.Model):
    _inherit = "res.users"

    allowed_edit_governance_ids = fields.Many2many(
        "governance.circle",
        compute="_compute_allowed_edit_governance_ids",
    )

    def _compute_allowed_edit_governance_ids(self):
        """Write access of active user:
        - His own roles
        - If the user belongs to a role flagged as 'Enabled Edit Circle',
          he is allowed to edit the parent circle of that role and all
          roles and circles within it.
        - If no editable role assigned and he is assigned to steering role of that
        circle,
          or
        - There is no editable roles, no steering role in the current circle,
          but he is assigned to steering role of the upper circle.
        """
        steering_role = self.env.ref(
            "hr_governance.steering_gct", raise_if_not_found=False
        )
        for user in self:
            user_roles = self._get_user_roles(user.id)
            if not user_roles:
                user.allowed_edit_governance_ids = [Command.clear()]
                continue

            # cache all records per role
            hierarchy_records_per_role = {}
            for role in user_roles:
                circle = role.parent_id
                hierarchy_records_per_role[role.id] = circle._get_hierarchy_records(
                    include_self=True
                ).filtered_domain([("is_circle", "=", True)])

            # roles that marked as 'Enable Edit Circle'
            enabled_edit_roles = user_roles.filtered_domain(
                [("type_id.enable_edit_circle", "=", True)]
            )
            editable_records = self.env[
                "governance.circle"
            ]._get_editable_records_from_roles(
                self.id, enabled_edit_roles, hierarchy_records_per_role
            )

            # steering roles act as catch-up
            steering_roles = user_roles.filtered_domain(
                [("type_id", "=", steering_role.id)]
            )
            editable_records |= self.env[
                "governance.circle"
            ]._get_editable_records_from_steering(
                steering_roles, hierarchy_records_per_role
            )

            user.allowed_edit_governance_ids = [Command.clear()] + [
                Command.link(record.id) for record in editable_records
            ]

    def _get_user_roles(self, user_id):
        return self.env["governance.circle"].search(
            [("member_rel_ids.member_id.user_id", "=", user_id)]
        )
