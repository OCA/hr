# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    passport_ids = fields.One2many(
        comodel_name='hr.employee.passport',
        inverse_name='employee_id',
        string="Passports",
    )
