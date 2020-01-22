# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployee(models.Model):

    _inherit = "hr.employee"

    no_autoclose = fields.Boolean(string="Don't Autoclose Attendances")
