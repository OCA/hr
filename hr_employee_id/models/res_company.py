# -*- coding: utf-8 -*-
# © 2015 Salton Massally <smassally@idtlabs.sl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    employee_id_gen_method = fields.Selection(
        [
            ('random', 'Random'),
            ('sequence', 'Sequence'),
        ],
        string="ID Generation Method",
        default='random'
    )
    employee_id_random_digits = fields.Integer(
        '# of Digits', default=5,
        help="Number of digits making up the ID"
    )
    employee_id_sequence = fields.Many2one(
        'ir.sequence', 'Sequence',
        help="Pattern to be used for used for ID Generation",
    )
