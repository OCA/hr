# Copyright 2020 Pavlov Media
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    split_attendance = fields.Boolean(
        string="Split Attendance",
        help="Split attendance into two start/end times cross over midnight.")
