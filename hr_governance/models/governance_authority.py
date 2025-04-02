# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class GovernanceAuthority(models.Model):
    _name = "governance.authority"
    _description = "Governance Authority"

    name = fields.Text(required=True)

    _sql_constraints = [
        (
            "unique_authority",
            "unique(name)",
            "This Authority already exists",
        ),
    ]
