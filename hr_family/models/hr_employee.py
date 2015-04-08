# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp import models, fields


class hr_employee(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    fam_spouse = fields.Char("Name", size=256)
    fam_spouse_employer = fields.Char("Employer", size=256)
    fam_spouse_tel = fields.Char("Telephone.", size=32)
    fam_children_ids = fields.One2many(
        'hr.employee.children', 'employee_id', "Children")
    fam_father = fields.Char("Father's Name", size=128)
    fam_father_dob = fields.Date("Date of Birth")
    fam_mother = fields.Char("Mother's Name", size=128)
    fam_mother_dob = fields.Date("Date of Birth")
