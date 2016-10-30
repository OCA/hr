# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields
from openerp.tools.translate import _


class HrContractInputType(models.Model):
    _name = "hr.contract.input_type"
    _description = "Contract Input Type Policy"

    contract_id = fields.Many2one(
        string="Contract",
        comodel_name="hr.contract",
        required=True,
        ondelete="cascade",
    )
    input_type_id = fields.Many2one(
        string="Input Type",
        comodel_name="hr.payslip.input_type",
        required=True,
        ondelete="restrict",
    )
    amount = fields.Float(
        string="Amount",
        require=True,
    )
    _sql_constraints = [
        ("contract_input_type_unique",
         "unique(contract_id, input_type_id)",
         _("No duplicate input type"))
    ]


class HrContract(models.Model):
    _inherit = "hr.contract"

    input_type_ids = fields.One2many(
        string="Input Types",
        comodel_name="hr.contract.input_type",
        inverse_name="contract_id",
    )
