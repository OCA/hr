# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields
from openerp.tools.translate import _


class HrPayslipInputType(models.Model):
    _name = "hr.payslip.input_type"
    _description = "Payslip Input Type"

    name = fields.Char(
        string="Input Type",
        required=True,
        translate=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    description = fields.Text(
        string="Description",
        translate=True,
    )

    _sql_constraints = [
        ("code_unique", "unique(code)", _("Code has to be unique)")),
    ]
