# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class GovernanceExpectation(models.Model):
    _name = "governance.expectation"
    _description = "Governance Expectation"

    name = fields.Text(required=True)
