# -*- coding: utf-8 -*-
# Copyright 2015 Salton Massally
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrContractType(models.Model):
    _inherit = 'hr.contract.type'

    trial_length = fields.Integer(
        help="Default contract trial length in Days"
    )
