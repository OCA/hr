# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    governance_assignment_ids = fields.One2many(
        "governance.circle.member.rel",
        "member_id",
        string="Governance Assignments",
    )
