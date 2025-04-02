# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import random

from odoo import Command, _, api, fields, models
from odoo.exceptions import AccessError, UserError
from odoo.tools import html_to_inner_content
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
    # assigned members for circle
    member_ids = fields.Many2manyCustom(
        "hr.employee",
        "governance_circle_member_rel",
        "circle_id",
        "member_id",
        create_table=False,
        string="Members",
        compute="_compute_member_ids",
    )
    # assigned members for role
    member_rel_ids = fields.One2many("governance.circle.member.rel", "circle_id")
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
    type_name = fields.Selection(related="type_id.type")
    is_steering_role = fields.Boolean(related="type_id.is_steering_role")
    purpose = fields.Html(
        compute="_compute_fields_from_type",
        readonly=False,
        store=True,
        string="Raison d'être",
    )
    # technical fields to store input from user
    user_input_purpose = fields.Text(compute="_compute_user_input_purpose", store=True)
    track_purpose = fields.Text(
        compute="_compute_tracking_fields",
        tracking=True,
        store=True,
        string="Raison d'être",
    )
    authority = fields.Html(
        compute="_compute_fields_from_type",
        readonly=False,
        store=True,
        string="Domain of authority",
    )
    authority_ids = fields.Many2many(
        comodel_name="governance.authority",
    )
    # technical fields to store input from user
    user_input_authority = fields.Html(
        compute="_compute_user_input_authority", store=True
    )
    track_authority = fields.Text(
        compute="_compute_tracking_fields",
        tracking=True,
        store=True,
        string="Domain of authority",
    )
    expectation_ids = fields.Many2many(
        comodel_name="governance.expectation",
    )
    expectation = fields.Html(
        compute="_compute_fields_from_type",
        readonly=False,
        store=True,
        string="Expectations",
    )
    # technical fields to store input from user
    user_input_expectation = fields.Text(
        compute="_compute_user_input_expectation", store=True
    )
    track_expectation = fields.Text(
        compute="_compute_tracking_fields",
        tracking=True,
        store=True,
        string="Expectations",
    )
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

    _sql_constraints = [
        (
            "unique_circle_and_role",
            "unique(name, parent_id)",
            "This Circle/Role already exists",
        ),
    ]

    @api.depends("purpose", "authority", "expectation")
    def _compute_tracking_fields(self):
        for rec in self:
            rec.track_purpose = html_to_inner_content(rec.purpose)
            rec.track_authority = html_to_inner_content(rec.authority)
            rec.track_expectation = html_to_inner_content(rec.expectation)

    @api.depends("member_ids", "member_rel_ids")
    def _compute_assigned_user_ids(self):
        for rec in self:
            if rec.member_ids:
                rec.assigned_user_ids = rec.member_ids.user_id
            elif rec.member_rel_ids:
                rec.assigned_user_ids = rec.member_rel_ids.member_id.user_id
            else:
                rec.assigned_user_ids = False

    def _compute_user_input_field(self, field_name, template_field_name):
        for rec in self:
            if not rec.type_id or not getattr(rec, field_name):
                setattr(rec, f"user_input_{field_name}", "")
                continue
            elif self.env.context.get("skip_update_user_input"):
                continue
            from_template = html_to_inner_content(
                getattr(rec.type_id, template_field_name)
            )
            existing = html_to_inner_content(getattr(rec, field_name))
            cleaned_existing = existing.replace(from_template, "")
            setattr(rec, f"user_input_{field_name}", cleaned_existing)

    @api.depends("purpose")
    def _compute_user_input_purpose(self):
        self._compute_user_input_field(
            field_name="purpose", template_field_name="purpose"
        )

    @api.depends("expectation")
    def _compute_user_input_expectation(self):
        self._compute_user_input_field(
            field_name="expectation", template_field_name="expectation"
        )

    @api.depends("authority")
    def _compute_user_input_authority(self):
        self._compute_user_input_field(
            field_name="authority", template_field_name="authority"
        )

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

    @api.depends("child_ids")
    def _compute_member_ids(self):
        for rec in self:
            rec.member_ids = rec.child_ids.member_rel_ids.mapped("member_id")

            # include member of steering roles of its subcircles
            # only the next level, not the whole hiearchy
            steering_roles = rec.child_ids.child_ids.filtered(
                lambda x: not x.is_circle and x.is_steering_role
            )
            rec.member_ids |= steering_roles.member_rel_ids.mapped("member_id")

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
            is_manager = self.env.user.user_has_groups(
                "hr_governance.governance_group_manager"
            )
            if only_manager_change_color and not is_manager:
                rec.is_color_field_invisible = True
            else:
                rec.is_color_field_invisible = is_greyscale_mode_on and rec.is_circle
                if not is_greyscale_mode_on:
                    rec.is_color_field_invisible = False

    @api.model
    def _get_default_color(self):
        """List of colors can be found in static/src/components/circlepack_colorlist.js
        By default,
            - a circle gets a random color (except white)
            - a role gets White unless its type is assigned with color
        """
        return random.randint(2, 11)

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

                if not rec.user_input_purpose:
                    rec.purpose = rec.type_id.purpose

                if not rec.user_input_expectation:
                    rec.expectation = rec.type_id.expectation

                if not rec.user_input_authority:
                    rec.authority = rec.type_id.authority

    @api.depends("type_id.type")
    def _compute_is_editable(self):
        for rec in self:
            rec.is_editable = not rec.type_id or rec.type_id.type == "template"

    @api.depends("is_circle")
    def _compute_is_addable(self):
        for rec in self:
            is_single_mode_on = str2bool(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("hr_governance.governance_single_assignee_mode")
            )
            if is_single_mode_on:
                rec.is_addable = not rec.is_circle and not rec.member_ids
            else:
                rec.is_addable = True

    @api.depends("member_ids")
    def _compute_member_count(self):
        for rec in self:
            rec.member_count = len(rec.member_ids)

    @api.constrains("parent_id", "is_root")
    def _check_parent_set(self):
        for rec in self:
            if not rec.is_root and not rec.parent_id:
                raise UserError(_("Parent must be set"))

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

        records = super().create(vals)

        return records

    def _get_circle_and_role_fields(self):
        return [
            "name",
            "member_ids",
            "member_rel_ids",
            "parent_id",
            "member_count",
            "id",
            "color",
            "is_circle",
            "type_name",
            "shape_type",
        ]

    # TODO: take advantage of hierarchy_read from native
    @api.model
    def get_hierarchy_data(self, domain):
        """Used to populate circle packing chart"""
        root = self.search([("parent_id", "=", False)], limit=1)
        records = self.search(domain)
        fields = self._get_circle_and_role_fields()
        records |= root

        result = records.read(fields)
        return result

    def write(self, vals):
        context = self.env.context
        forbidden_fields = self._get_forbidden_change_fields()
        if forbidden_fields and not context.get("skip_update_user_input"):
            self._sanity_check(forbidden_fields, vals)

        # Permission constraint
        allowed_to_edit = (
            self.env.su
            or self.id in self.env.user.allowed_edit_governance_ids.ids
            or self.env.user.user_has_groups("hr_governance.governance_group_manager")
        )
        if not allowed_to_edit:
            if self.is_circle:
                editable_roles = [
                    role["name"] for role in self.type_id._get_enable_edit_circle_role()
                ]
                names = ", ".join(editable_roles)
                raise AccessError(_("Only %s can edit this Circle") % names)
            raise AccessError(_("You cannot edit this Role"))

        res = super().write(vals)
        return res

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
                    existing = html_to_inner_content(value_list[field])
                    error = from_template and from_template not in existing
                    if error:
                        errors.append(field_name)

        if len(errors) > 0:
            raise UserError(
                _(
                    "You can only add content at the end of %s created from a "
                    "template.",
                    ", ".join(errors),
                )
            )

    def _get_forbidden_change_fields(self):
        forbidden_keys = ["expectation", "authority", "purpose"]
        return forbidden_keys

    def _get_hierarchy_records(self, reverse=False, include_self=False):
        """Return the hiearchy records in ``self`` based on reverse direction.

        :param reverse: If True, returns parent records.
        By default, return child records
        """
        result = self.browse(
            set.union(
                set(), *self._get_role_ids_per_circle_id(reverse=reverse).values()
            )
        )
        if include_self:
            return self | result
        return result

    def _get_role_ids_per_circle_id(self, reverse):
        return {rec.id: rec._get_roles_recursively(reverse=reverse).ids for rec in self}

    def _get_roles_recursively(self, reverse):
        roles = self.parent_id if reverse else self.child_ids
        if not roles:
            return self.env["governance.circle"]
        return roles + roles._get_roles_recursively(reverse)

    def unlink(self):
        # Add roles to batch of records to delete
        records = self._get_hierarchy_records(include_self=True)
        # sorted to process child first
        self = records.sorted(key=lambda x: x.id, reverse=True)
        for rec in self:
            if rec.member_rel_ids:
                rec.member_rel_ids.unlink()
        return super().unlink()

    @api.model
    def js_get_deleted_circle_info(self, circle_id):
        result = {}
        if circle_id:
            circle = self.browse(circle_id)
            children = circle._get_hierarchy_records()
            result.update(
                {
                    "subcircles": len(children.filtered("is_circle").ids),
                    "roles": len(children.filtered(lambda x: not x.is_circle).ids),
                    "employees": len(children.member_rel_ids.ids),
                }
            )
        return result

    def _is_assigned(self):
        self.ensure_one()
        return (
            self.is_circle
            and self.child_ids.search_count(
                [
                    ("parent_id", "=", self.id),
                    ("type_id.enable_edit_circle", "=", True),
                    ("member_rel_ids", "!=", False),
                ],
            )
            > 0
        )

    def _is_assigned_w_steering(self):
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
                    ("member_rel_ids", "!=", False),
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
            steering |= self._get_hierarchy_records(include_self=True).filtered_domain(
                domain
            )
        user_ids = steering.member_rel_ids.member_id.mapped("user_id").ids
        return user_ids if user_ids else []

    @api.model
    def _get_editable_records_from_steering(self, roles, lookup):
        all_records = editable_records = excluded_records = self
        for role in roles:
            hierarchy_records = lookup.get(role.id, self)
            all_records |= hierarchy_records

        for record in all_records:
            if not record._is_assigned():
                editable_records |= record | record.child_ids.filtered_domain(
                    [("is_circle", "=", False)]
                )
                # exclude it when its parent is assigned
                # only member belonging to parent is allowed
                if record.parent_id in all_records and record.parent_id._is_assigned():
                    excluded_records |= record | record.child_ids
        return editable_records - excluded_records

    @api.model
    def _get_editable_records_from_roles(self, user_id, roles, lookup):
        all_records = editable_records = excluded_records = self
        for role in roles:
            hierarchy_records = lookup.get(role.id, self)
            all_records |= hierarchy_records

        for record in all_records:
            is_member = user_id in record.member_ids.mapped("user_id").ids
            is_member_of_parent = (
                user_id in record.parent_id.member_ids.mapped("user_id").ids
            )
            if not record._is_assigned() and (
                record._is_assigned_w_steering()
                or (
                    record.parent_id._is_assigned_w_steering()
                    and not is_member_of_parent
                )
            ):
                excluded_records |= record | record.child_ids

            elif (record._is_assigned() and is_member) or not record._is_assigned():
                editable_records |= record | record.child_ids.filtered_domain(
                    [("is_circle", "=", False)]
                )
        return editable_records - excluded_records
