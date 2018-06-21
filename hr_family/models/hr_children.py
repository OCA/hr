# Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


GENDER_SELECTION = [('male', 'Male'),
                    ('female', 'Female')]


class HrChildren(models.Model):
    _name = 'hr.employee.children'
    _description = 'HR Employee Children'

    name = fields.Char(
        string="Name",
        required=True
    )
    date_of_birth = fields.Date(
        string="Date of Birth",
        oldname='dob'
    )
    employee_id = fields.Many2one(
        string="Employee",
        comodel_name='hr.employee',
    )
    gender = fields.Selection(
        string='Gender',
        selection=GENDER_SELECTION
    )
