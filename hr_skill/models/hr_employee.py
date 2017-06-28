# -*- coding: utf-8 -*-
# ©  2015 iDT LABS (http://www.@idtlabs.sl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
