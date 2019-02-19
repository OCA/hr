# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    theoretical_hours_start_date = fields.Date(
        help="Fill this field for setting a manual start date for computing "
             "the theoretical hours independently from the attendances. If "
             "not filled, employee creation date or the calendar start date "
             "will be used (the greatest of both).",
    )
