# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    marital_status_id = fields.Many2one(
        'hr.employee.marital.status', string='Marital status',
    )
