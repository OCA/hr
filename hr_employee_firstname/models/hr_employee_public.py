# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    # Fields coming from hr.employee.base
    firstname = fields.Char(readonly=True)
    lastname = fields.Char(readonly=True)
