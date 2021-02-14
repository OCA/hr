# Copyright 2021 Iryna Vyshnevska (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    work_permit_ids = fields.One2many(
        string="Work permit",
        comodel_name="hr.employee.workpermit",
        inverse_name="employee_id",
    )
    marital_status_ids = fields.One2many(
        string="Marital status",
        comodel_name="hr.employee.marital",
        inverse_name="employee_id",
    )
