# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import ormcache
from odoo.tools.mail import append_content_to_html


class GovernanceRoleType(models.Model):
    _name = "governance.role.type"
    _description = "Governance Role Type"

    name = fields.Char(required=True)
    type = fields.Selection(
        [("template", "Template"), ("structure", "Structure")], required=True
    )
    purpose = fields.Html(
        string="Raison d'être",
    )
    authority = fields.Html(
        string="Domain of authorities",
    )
    expectation = fields.Html(
        string="Expectations",
    )
    color = fields.Integer(default=1)
    is_steering_role = fields.Boolean(default=False)
    source_circle_id = fields.Many2one(
        "governance.circle",
        default=lambda x: x._get_default_source_circle_id(),
        domain="[('is_circle', '=', True)]",
        help="This Role Type are only allowed in the Source Circle and its children",
    )

    enable_edit_circle = fields.Boolean(
        help="If checked, member of this Role type is allowed to modify Circle"
    )
    _sql_constraints = [
        (
            "unique_role_type",
            "unique(name)",
            "This Circle Type already exists",
        ),
    ]

    def _get_default_source_circle_id(self):
        root_circle = self.env.ref(
            "hr_governance.root", raise_if_not_found=False
        ) or self.env["governance.circle"].search([("is_root", "=", True)])
        return root_circle or False

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        self.env.registry.clear_cache()
        return records

    def _update_governance_circle(self, field_name, template_value):
        if not template_value:
            return
        roles = self.env["governance.circle"].search([("type_id", "=", self.id)])
        for role in roles.with_context(skip_update_user_input=True):
            user_input = getattr(role, f"user_input_{field_name}")
            updated = append_content_to_html(
                template_value, user_input, plaintext=False
            )
            role.write({field_name: updated})

    @api.model
    @ormcache()
    def _get_structuring_role_vals(self):
        templates = self.env["governance.role.type"].search(
            [("type", "=", "structure")]
        )
        return [
            {"type_id": temp.id, **temp._required_role_fields()} for temp in templates
        ]

    @api.model
    @ormcache()
    def _get_enable_edit_circle_role(self):
        roles = self.env["governance.role.type"].search(
            [("enable_edit_circle", "=", True)]
        )
        return [{"id": role.id, "name": role.name} for role in roles]

    def write(self, vals):
        res = super().write(vals)
        if "purpose" in vals:
            self._update_governance_circle("purpose", vals.get("purpose", ""))
        if "expectation" in vals:
            self._update_governance_circle("expectation", vals.get("expectation", ""))
        if "authority" in vals:
            self._update_governance_circle("authority", vals.get("authority", ""))
        if any(field in vals for field in ["enable_edit_circle", "type"]):
            self.env.registry.clear_cache()
        return res

    def unlink(self):
        res = super().unlink()
        self.env.registry.clear_cache()
        return res

    def _required_role_fields(self):
        return {
            "name": self.name,
            "color": self.color,
            "purpose": self.purpose,
            "authority": self.authority,
            "expectation": self.expectation,
        }
