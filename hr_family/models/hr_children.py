# -*- coding: utf-8 -*-
# Copyright (C) 2011, 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields

GENDER_SELECTION = [('male', 'Male'),
                    ('female', 'Female'),
                    ('other', 'Other')]


class HrChildren(models.Model):
    _name = 'hr.employee.children'
    _description = 'HR Employee Children'

    name = fields.Char("Name", required=True)
    date_of_birth = fields.Date("Date of Birth", oldname='dob')
    employee_id = fields.Many2one('hr.employee', "Employee")
    gender = fields.Selection(selection=GENDER_SELECTION, string='Gender')
