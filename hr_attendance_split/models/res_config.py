# Copyright 2020 Pavlov Media
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    split_attendance = fields.Boolean(
        string="Split Attendance",
        related='company_id.split_attendance',
        help="Split attendance into two start/end times cross over midnight.",
        readonly=False)
