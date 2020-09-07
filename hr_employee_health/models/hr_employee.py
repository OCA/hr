# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    health_condition_ids = fields.One2many(
        string="Health Conditions",
        comodel_name="hr.employee.health.condition",
        inverse_name="employee_id",
        groups="hr.group_hr_user",
        help="Health condition of an employee.",
    )
    blood_type_id = fields.Many2one(
        string="Blood Type",
        comodel_name="hr.employee.blood.type",
        groups="hr.group_hr_user",
        help="Blood group of an employee.",
    )
    health_notes = fields.Text(
        string="Health Notes",
        groups="hr.group_hr_user",
        help="Employees health related notes.",
    )
