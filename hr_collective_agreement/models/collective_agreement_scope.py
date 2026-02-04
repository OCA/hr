# Copyright 2025 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CollectiveAgreementScope(models.Model):
    _name = "collective.agreement.scope"
    _description = "Collective Agreement Scope"

    name = fields.Char(required=True)

    _sql_constraints = [("name_uniq", "unique(name)", "The name must be unique.")]
