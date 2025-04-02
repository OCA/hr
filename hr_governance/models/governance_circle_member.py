# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class GovernanceCircleMember(models.Model):
    _name = "governance.circle.member.rel"
    _description = "Roles and Members relation"
    _rec_names_search = ["member_id.name"]

    circle_id = fields.Many2one(
        "governance.circle", string="Governance Circle", required=True, index=True
    )
    member_id = fields.Many2one(
        "hr.employee", string="Energized by", required=True, index=True
    )
    percentage = fields.Float(string="Time dedicated (%)")
    focus = fields.Text()
    _sql_constraints = [
        (
            "unique_member_per_role",
            "unique(member_id, circle_id)",
            "This member is already assigned to the role/circle",
        ),
    ]
