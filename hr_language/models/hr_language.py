# -*- coding: utf-8 -*-
# Copyright (C) 2017-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, tools


class HrLanguage(models.Model):
    _name = 'hr.language'

    name = fields.Selection(
        tools.scan_languages(),
        "Language",
        required=True,
    )
    description = fields.Char(
        "Description",
        size=64,
        required=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        "Employee",
        required=True,
    )
    can_read = fields.Boolean(
        "Read",
        default=True,
        oldname='read',
    )
    can_write = fields.Boolean(
        "Write",
        default=True,
        oldname='write',
    )
    can_speak = fields.Boolean(
        "Speak",
        default=True,
        oldname='speak',
    )
