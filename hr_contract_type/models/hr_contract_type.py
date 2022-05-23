# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractType(models.Model):
    _name = "hr.contract.type"
    _description = "Contract Type"

    name = fields.Char(required=True)
