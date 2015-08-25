# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2015 Salton Massally (<smassally@idtlabs.sl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

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
