# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class HrEmployeeIdentificationType(models.Model):
    _name = 'hr.employee.identification.type'
    _description = 'Identification/Passport'
    _order = 'name'

    name = fields.Char(required=True)
