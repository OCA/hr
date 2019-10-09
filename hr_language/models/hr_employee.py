# -*- coding: utf-8 -*-
# Copyright (C) 2017-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    language_ids = fields.One2many(
        'hr.language',
        'employee_id',
        "Languages",
        help="Languages of this employee",
    )
