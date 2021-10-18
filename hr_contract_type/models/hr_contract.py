# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrContract(models.Model):

    _inherit = "hr.contract"

    contract_type_id = fields.Many2one("hr.contract.type", "Contract Type")
