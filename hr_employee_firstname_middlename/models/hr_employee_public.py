# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    # Field coming from hr.employee.base
    middle_name = fields.Char(readonly=True)
