# Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


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
