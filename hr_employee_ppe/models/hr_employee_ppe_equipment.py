# Copyright 2020 Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployeePpeEquipment(models.Model):

    _name = 'hr.employee.ppe.equipment'
    _description = 'Personal Protective Equipments - Equipment List'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Equipment')
    expirable = fields.Boolean()
