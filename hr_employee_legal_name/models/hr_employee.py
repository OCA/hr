# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of hr_employee_legal_name,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     hr_employee_legal_name is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     hr_employee_legal_name is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with hr_employee_legal_name.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    different_legal_name = fields.Boolean()
    legal_name = fields.Char()

    @api.onchange('different_legal_name')
    @api.one
    def on_change_different_legal_name(self):
        if not self.different_legal_name:
            self.legal_name = False
