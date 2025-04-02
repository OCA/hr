# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    circle_ids = fields.Many2manyCustom(
        "governance.circle",
        "governance_circle_member_rel",
        "member_id",
        "circle_id",
        create_table=False,
        string="Governance Circle",
    )
