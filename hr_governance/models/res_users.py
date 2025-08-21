# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Users(models.Model):
    _inherit = "res.users"

    allowed_edit_governance_ids = fields.Many2many(
        "governance.circle",
        compute="_compute_allowed_edit_governance_ids",
    )

    def _compute_allowed_edit_governance_ids(self):
        """
        Computes the governance circles and roles a user is allowed to edit.

        A user's edit permissions are determined by the roles they are assigned to.
        The logic gives precedence to roles with specific 'Enable Edit Circle'
        permissions, and uses 'Steering' roles as a fallback.

        1.  **Roles with "Enable Edit Circle" permission**:
            If a user is a member of a role with `enable_edit_circle` set to True,
            they gain edit rights over the role's parent circle and all its
            descendants (sub-circles and roles). This right is only granted if the
            circle is not already managed by another "edit-enabled" role assigned
            to a different user.

        2.  **"Steering" Role as a fallback**:
            If a circle does not have an assigned "edit-enabled" role, members of
            the "Steering" role within that circle (or an ancestor circle) may gain
            edit rights. This acts as a fallback mechanism.

        3.  **Direct Role Membership**:
            Users can always edit the specific roles they are directly assigned to.

        4.  **Managers**:
            Users with "Manager" access in the Governance module can edit all
            circles and roles.
        """
        steering_role_type = self.env.ref(
            "hr_governance.steering_gct", raise_if_not_found=False
        )
        governance_circle_model = self.env["governance.circle"]

        for user in self:
            if user.has_groups("hr_governance.governance_group_manager"):
                user.allowed_edit_governance_ids = governance_circle_model.search([])
                continue

            user_roles = governance_circle_model.search(
                [("member_rel_ids.member_id.user_id", "=", user.id)]
            )
            if not user_roles:
                user.allowed_edit_governance_ids = []
                continue

            # Build a lookup map of all circles affected by the user's roles.
            # For each role, this includes the parent circle and all its descendants.
            circles_per_role = {}
            for role in user_roles:
                circle = role.parent_id
                circles_per_role[role.id] = circle._get_descendants(
                    include_self=True
                ).filtered("is_circle")

            # 1. Get circles editable via roles with 'enable_edit_circle' permission.
            permission_roles = user_roles.filtered("type_id.enable_edit_circle")
            editable_circles = (
                governance_circle_model._get_editable_circles_for_permission_roles(
                    user, permission_roles, circles_per_role
                )
            )

            # 2. Get circles editable via steering roles as a fallback.
            steering_roles = user_roles.filtered(
                lambda r: r.type_id == steering_role_type
            )
            editable_circles |= (
                governance_circle_model._get_editable_circles_for_steering_roles(
                    steering_roles, circles_per_role
                )
            )

            # 3. Users can always edit the roles they are assigned to.
            editable_circles |= user_roles

            user.allowed_edit_governance_ids = editable_circles
