# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import random

from odoo import Command, _, api, fields, models
from odoo.exceptions import AccessError, UserError
from odoo.tools.mail import html_to_inner_content
from odoo.tools.misc import str2bool


class GovernanceCircle(models.Model):
    _name = "governance.circle"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Governance Circle and Roles"
    _parent_store = True

    name = fields.Char(
        tracking=True,
        required=True,
        readonly=False,
        compute="_compute_fields_from_type",
        store=True,
    )
    parent_id = fields.Many2one(
        "governance.circle",
        ondelete="restrict",
        index=True,
        domain=[("is_circle", "=", True)],
    )
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many(
        "governance.circle",
        "parent_id",
    )
    # For roles:
    role_assignment_ids = fields.One2many(
        "governance.circle.member.rel", "circle_id", string="Role Assignments"
    )
    # For circles:
    circle_member_ids = fields.Many2many(
        "hr.employee",
        string="Circle Members",
        compute="_compute_circle_member_ids",
        store=True,
    )
    assigned_user_ids = fields.Many2many(
        "res.users", compute="_compute_assigned_user_ids", string="Assigned Users"
    )
    member_count = fields.Integer(compute="_compute_member_count")
    type_id = fields.Many2one(
        "governance.role.type",
        tracking=True,
        ondelete="restrict",
        domain="[('id','in', suitable_type_ids)]",
    )
    suitable_type_ids = fields.Many2many(
        "governance.role.type", compute="_compute_suitable_type_ids", recursive=True
    )
    role_type_name = fields.Selection(related="type_id.type", string="Role Type Name")
    is_steering_role = fields.Boolean(related="type_id.is_steering_role")
    is_editable = fields.Boolean(compute="_compute_is_editable")
    is_addable = fields.Boolean(compute="_compute_is_addable")
    color = fields.Integer(
        compute="_compute_fields_from_type",
        readonly=False,
        store=True,
        default=lambda self: self._get_default_color(),
    )
    is_circle = fields.Boolean(compute="_compute_is_circle", store=True)
    is_color_field_invisible = fields.Boolean(
        compute="_compute_is_color_field_invisible",
    )
    is_root = fields.Boolean(default=False)
    shape_type = fields.Selection(
        [("circle", "Circle"), ("hexagon", "Hexagon")],
        string="Shape",
        default="circle",
    )

    ##########################################################################
    # Content fields
    ##########################################################################
    purpose = fields.Html(
        compute="_compute_fields_from_type",
        readonly=False,
        store=True,
    )
    authority = fields.Html(
        compute="_compute_fields_from_type",
        readonly=False,
        store=True,
    )
    expectation = fields.Html(
        compute="_compute_fields_from_type",
        readonly=False,
        store=True,
    )
    # duplicate fields for tracking
    purpose_tracking = fields.Text(
        compute="_compute_tracking_fields",
        store=True,
        tracking=True,
        string="Raison d'être",
    )
    authority_tracking = fields.Text(
        compute="_compute_tracking_fields",
        store=True,
        tracking=True,
        string="Domain of authority",
    )
    expectation_tracking = fields.Text(
        compute="_compute_tracking_fields",
        store=True,
        tracking=True,
        string="Expectations",
    )

    _sql_constraints = [
        (
            "unique_circle_and_role",
            "unique(name, parent_id)",
            "This Circle/Role already exists",
        ),
    ]

    @api.constrains("parent_id", "is_root")
    def _check_parent_set(self):
        for rec in self:
            if not rec.is_root and not rec.parent_id:
                raise UserError(_("Parent must be set"))

    ##########################################################################
    # Computed methods
    ##########################################################################
    @api.depends("purpose", "authority", "expectation")
    def _compute_tracking_fields(self):
        for rec in self:
            rec.purpose_tracking = (
                html_to_inner_content(rec.purpose) if rec.purpose else ""
            )
            rec.authority_tracking = (
                html_to_inner_content(rec.authority) if rec.authority else ""
            )
            rec.expectation_tracking = (
                html_to_inner_content(rec.expectation) if rec.expectation else ""
            )

    @api.depends("role_assignment_ids.member_id.user_id", "circle_member_ids.user_id")
    def _compute_assigned_user_ids(self):
        for rec in self:
            if rec.is_circle:
                rec.assigned_user_ids = rec.circle_member_ids.user_id
            else:
                rec.assigned_user_ids = rec.role_assignment_ids.member_id.user_id

    @api.depends("parent_id", "parent_id.suitable_type_ids")
    def _compute_suitable_type_ids(self):
        for rec in self:
            if rec.parent_id:
                rec.suitable_type_ids = self.env["governance.role.type"].search(
                    [
                        ("source_circle_id", "=", rec.parent_id.id),
                    ]
                )
                rec.suitable_type_ids |= rec.parent_id.suitable_type_ids
            else:
                rec.suitable_type_ids = [Command.clear()]

    @api.depends(
        "is_circle",
        "child_ids.role_assignment_ids",
        "child_ids.child_ids.role_assignment_ids",
    )
    def _compute_circle_member_ids(self):
        for rec in self.filtered("is_circle"):
            # Get members from direct child roles
            members = rec.child_ids.role_assignment_ids.mapped("member_id")
            # Include members of steering roles of its sub-circles
            # (only the next level, not the whole hierarchy)
            steering_roles = rec.child_ids.child_ids.filtered(
                lambda r: not r.is_circle and r.is_steering_role
            )
            members |= steering_roles.role_assignment_ids.mapped("member_id")
            rec.circle_member_ids = members
        for rec in self.filtered(lambda c: not c.is_circle):
            rec.circle_member_ids = False

    @api.depends("is_circle")
    def _compute_is_color_field_invisible(self):
        """Field Color on Form is visible when
        param only_manager_change_color = 1
            - only Manager can see it
        param only_manager_change_color = 0
            - everyone can see it

        When greyscale mode is on:
            - user can only see the field when it is a role
            - a circle gets dark gray color
        """
        is_greyscale_mode_on = self.get_greyscale_mode_param()
        only_manager_change_color = str2bool(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("hr_governance.only_manager_change_color")
        )
        for rec in self:
            is_manager = self.env.user.has_groups(
                "hr_governance.governance_group_manager"
            )
            if only_manager_change_color and not is_manager:
                rec.is_color_field_invisible = True
            else:
                rec.is_color_field_invisible = is_greyscale_mode_on and rec.is_circle
                if not is_greyscale_mode_on:
                    rec.is_color_field_invisible = False

    @api.depends("child_ids", "is_root")
    def _compute_is_circle(self):
        for rec in self:
            rec.is_circle = len(rec.child_ids) or rec.is_root

    @api.depends(
        "is_circle",
        "type_id",
        "type_id.purpose",
        "type_id.name",
        "type_id.expectation",
        "type_id.authority",
        "type_id.color",
    )
    def _compute_fields_from_type(self):
        for rec in self:
            if rec.is_circle:
                rec.color = rec.color or rec._get_default_color()
            else:
                if not rec.type_id:
                    rec.color = rec.color or 1  # role is white by default
                    continue

                if not rec.name:
                    rec.name = rec.type_id.name

                if not rec.color:
                    rec.color = rec.type_id.color

                if not rec.purpose:
                    rec.purpose = rec.type_id.purpose

                if not rec.expectation:
                    rec.expectation = rec.type_id.expectation

                if not rec.authority:
                    rec.authority = rec.type_id.authority

    @api.depends("type_id.type")
    def _compute_is_editable(self):
        for rec in self:
            rec.is_editable = not rec.type_id or rec.type_id.type == "template"

    @api.depends("is_circle", "role_assignment_ids")
    def _compute_is_addable(self):
        for rec in self:
            is_single_mode_on = str2bool(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("hr_governance.governance_single_assignee_mode")
            )
            if is_single_mode_on:
                rec.is_addable = not rec.is_circle and not rec.role_assignment_ids
            else:
                rec.is_addable = True

    @api.depends("role_assignment_ids", "circle_member_ids")
    def _compute_member_count(self):
        for rec in self:
            if rec.is_circle:
                rec.member_count = len(rec.circle_member_ids)
            else:
                rec.member_count = len(rec.role_assignment_ids)

    ##########################################################################
    # Main methods
    ##########################################################################

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            context = self.env.context
            # auto create structuring roles for circle
            if context.get("default_is_circle", False):
                circle = self.new(val)
                new_roles_vals = circle.type_id._get_structuring_role_vals()
                existing_child_ids = val.get("child_ids", [])
                new_child_ids = existing_child_ids + [
                    (0, 0, val) for val in new_roles_vals
                ]
                val["child_ids"] = new_child_ids

        return super().create(vals)

    def write(self, vals):
        context = self.env.context
        forbidden_fields = self._get_forbidden_change_fields()
        if forbidden_fields and not context.get("skip_sanity_check"):
            self._sanity_check(forbidden_fields, vals)

        # Permission constraint
        allowed_to_edit = (
            self.env.su
            or self.id in self.env.user.allowed_edit_governance_ids.ids
            or self.env.user.has_groups("hr_governance.governance_group_manager")
        )
        if not allowed_to_edit:
            if self.is_circle:
                editable_roles = [
                    role["name"] for role in self.type_id._get_enable_edit_circle_role()
                ]
                names = ", ".join(editable_roles)
                raise AccessError(_("Only %s can edit this Circle", names))
            raise AccessError(_("You cannot edit this Role"))

        assigned_user_ids = self.mapped("assigned_user_ids")
        res = super().write(vals)
        notify_users = (
            assigned_user_ids | self.mapped("assigned_user_ids") - self.env.user
        )
        if notify_users:
            for user in notify_users:
                user._bus_send(
                    "circle_member_changed",
                    {
                        "type": "danger",
                        "title": _("Warning"),
                        "message": _(
                            "The Governance structure has been updated."
                            "Please refresh the page to view the latest changes."
                        ),
                    },
                )
        return res

    def unlink(self):
        # Add roles to batch of records to delete
        records = self._get_descendants(include_self=True)
        # sorted to process child first
        self = records.sorted(key=lambda x: x.id, reverse=True)
        for rec in self:
            if rec.is_root:
                raise UserError(_("Root Circle should not be deleted"))

            if rec.role_assignment_ids:
                rec.role_assignment_ids.unlink()
        return super().unlink()

    @api.model
    def _get_default_color(self):
        """List of colors can be found in static/src/components/circlepack_colorlist.js
        By default,
            - a circle gets a random color (except white)
            - a role gets White unless its type is assigned with color
        """
        return random.randint(2, 11)

    @api.model
    def get_greyscale_mode_param(self):
        is_greyscale_mode_on = str2bool(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("hr_governance.governance_check_grayscale")
        )
        return is_greyscale_mode_on

    @api.model
    def get_stripe_param(self):
        is_stripe_all_roles = str2bool(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("hr_governance.stripe_all_unassigned_roles")
        )
        return is_stripe_all_roles

    def _get_forbidden_change_fields(self):
        forbidden_keys = ["expectation", "authority", "purpose"]
        return forbidden_keys

    def _get_descendants(self, include_self=False):
        if not self:
            return self.env["governance.circle"]
        # This assumes a single record in self, which is how it's used.
        domain = [("parent_path", "=like", self.parent_path + "%")]
        if not include_self:
            domain.append(("id", "!=", self.id))
        return self.search(domain)

    @api.model
    def js_get_deleted_circle_info(self, circle_id):
        result = {}
        if circle_id:
            circle = self.browse(circle_id)
            children = circle._get_descendants()
            result.update(
                {
                    "subcircles": len(children.filtered("is_circle").ids),
                    "roles": len(children.filtered(lambda x: not x.is_circle).ids),
                    "employees": len(children.role_assignment_ids.ids),
                }
            )
        return result

    def _is_assigned(self):
        """Check if the circle has a role with 'enable_edit_circle' that is assigned."""
        self.ensure_one()
        return (
            self.is_circle
            and self.child_ids.search_count(
                [
                    ("parent_id", "=", self.id),
                    ("type_id.enable_edit_circle", "=", True),
                    ("role_assignment_ids", "!=", False),
                ],
            )
            > 0
        )

    def _is_assigned_w_steering(self):
        """Check if the circle has a steering role that is assigned."""
        self.ensure_one()
        steering_role = self.env.ref(
            "hr_governance.steering_gct", raise_if_not_found=False
        )
        return (
            steering_role
            and self.is_circle
            and self.child_ids.search_count(
                [
                    ("parent_id", "=", self.id),
                    ("type_id", "=", steering_role.id),
                    ("role_assignment_ids", "!=", False),
                ],
            )
            > 0
        )

    def _get_steering_role_user_ids(self):
        """Fetch user_ids of steering roles belonging to circle_id"""
        if not self:
            return []
        steering_role = self.env.ref(
            "hr_governance.steering_gct", raise_if_not_found=False
        )
        domain = [("type_id", "=", steering_role.id)]
        steering = self
        if self.is_circle:
            steering |= self.child_ids.filtered_domain(domain)
        else:
            # if it's role, retrieve steering roles of encompassing circle
            steering |= self._get_descendants(include_self=True).filtered_domain(domain)
        user_ids = steering.role_assignment_ids.member_id.mapped("user_id").ids
        return user_ids if user_ids else []

    @api.model
    def _get_editable_circles_for_steering_roles(self, steering_roles, circles_lookup):
        all_potential_circles = self.env["governance.circle"]
        for role in steering_roles:
            all_potential_circles |= circles_lookup.get(
                role.id, self.env["governance.circle"]
            )

        editable_circles = self.env["governance.circle"]
        excluded_circles = self.env["governance.circle"]

        for circle in all_potential_circles:
            # Circle is editable via steering role
            # if it has no assigned permission role.
            if not circle._is_assigned():
                editable_circles |= circle
                editable_circles |= circle.child_ids.filtered(lambda r: not r.is_circle)

                # Exclude the circle if its parent is already managed by a
                # permission role, as that takes precedence.
                if (
                    circle.parent_id in all_potential_circles
                    and circle.parent_id._is_assigned()
                ):
                    excluded_circles |= circle | circle.child_ids
        return editable_circles - excluded_circles

    @api.model
    def _get_editable_circles_for_permission_roles(
        self, user, permission_roles, circles_lookup
    ):
        all_potential_circles = self.env["governance.circle"]
        for role in permission_roles:
            all_potential_circles |= circles_lookup.get(
                role.id, self.env["governance.circle"]
            )

        editable_circles = self.env["governance.circle"]
        excluded_circles = self.env["governance.circle"]

        for circle in all_potential_circles:
            is_member = user.id in circle.circle_member_ids.user_id.ids
            is_member_of_parent = (
                user.id in circle.parent_id.circle_member_ids.user_id.ids
            )

            # Exclusion Rule: A circle is excluded if it has no permission role, but
            # a steering role is assigned (either in the circle itself, or in its
            # parent, and the user is not a member of the parent). This gives
            # precedence to the steering role holders.
            if not circle._is_assigned() and (
                circle._is_assigned_w_steering()
                or (
                    circle.parent_id._is_assigned_w_steering()
                    and not is_member_of_parent
                )
            ):
                excluded_circles |= circle | circle.child_ids

            # Inclusion Rule: A circle is editable if it has an assigned permission
            # role and the user is a member, OR if it has no assigned role at all
            # (and was not excluded by the rule above).
            elif (circle._is_assigned() and is_member) or not circle._is_assigned():
                editable_circles |= circle
                editable_circles |= circle.child_ids.filtered(lambda r: not r.is_circle)
        return editable_circles - excluded_circles

    ##########################################################################
    # Helpers
    ##########################################################################

    def _update_content(self, field_name, new_value, old_value):
        self.ensure_one()
        current_content = getattr(self, field_name) or ""
        # extract plan text from html
        current_content_plain = (
            html_to_inner_content(current_content) if current_content else ""
        )
        old_content_plain = html_to_inner_content(old_value) if old_value else ""

        user_input = ""
        if current_content_plain and old_content_plain:
            if current_content_plain.startswith(old_content_plain):
                # Extract everything after the old template
                user_input = current_content_plain[len(old_content_plain) :].strip()
            else:
                if old_content_plain in current_content_plain:
                    template_pos = current_content_plain.find(old_content_plain)
                    user_input = current_content_plain[
                        template_pos + len(old_content_plain) :
                    ].strip()
                else:
                    user_input = current_content_plain

        user_input = user_input.strip()
        if user_input:
            # append it to the new template
            new_content = new_value + "\n\n" + user_input
        else:
            new_content = new_value

        self.with_context(skip_sanity_check=True).write({field_name: new_content})

    def _sanity_check(self, forbidden_fields, value_list):
        """Sanity check for `write()`
        Validate that values of fields imported from template role
        are improperly modified
        """
        errors = []
        for field in forbidden_fields:
            if field in value_list.keys():
                field_name = self._fields[field].get_description(self.env)["string"]
                if isinstance(self._fields[field], fields.Html):
                    from_template = html_to_inner_content(getattr(self.type_id, field))
                    existing = value_list[field] or ""
                    if from_template and from_template not in existing:
                        errors.append(field_name)

        if len(errors) > 0:
            raise UserError(
                _(
                    "You can only add content at the end of %s created from a "
                    "template.",
                    ", ".join(errors),
                )
            )

    # TODO: take advantage of hierarchy_read from native
    @api.model
    def get_hierarchy_data(self, domain):
        """Used to populate circle packing chart"""
        final_domain = domain.extend([("is_root", "=", True)])
        result = self.search_read(
            final_domain, fields=self._get_circle_and_role_fields()
        )
        return result

    def _get_circle_and_role_fields(self):
        return [
            "name",
            "circle_member_ids",
            "role_assignment_ids",
            "parent_id",
            "member_count",
            "id",
            "color",
            "is_circle",
            "role_type_name",
            "shape_type",
        ]
