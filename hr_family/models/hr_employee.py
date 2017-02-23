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

from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    fam_spouse = fields.Char(string="Spouse's Name")
    fam_spouse_employer = fields.Char(string="Spouses's Employer")
    fam_spouse_tel = fields.Char(string="Spouse's Telephone")
    fam_children_ids = fields.One2many(
        string="Children",
        comodel_name='hr.employee.children',
        inverse_name='employee_id'
    )
    fam_father = fields.Char(string="Father's Name")
    fam_father_date_of_birth = fields.Date(
        string="Father Date of Birth",
        oldname='fam_father_dob'
    )
    fam_mother = fields.Char(string="Mother's Name")
    fam_mother_date_of_birth = fields.Date(
        string="Mother Date of Birth",
        oldname='fam_mother_dob'
    )
