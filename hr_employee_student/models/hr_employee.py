# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of hr_employee_student,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     hr_employee_student is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     hr_employee_student is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with hr_employee_student.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    student_card_number = fields.Char()
    student_card_expire_date = fields.Date()
