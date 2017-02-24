# -*- coding: utf-8 -*-
# Copyright 2013 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class Employee(models.Model):
    _inherit = 'hr.employee'

    skill_ids = fields.Many2many(
        'hr.skill',
        'skill_employee_rel',
        'employee_id',
        'skill_id',
        'Skills',
        domain="[('child_ids', '=', False)]",
    )
