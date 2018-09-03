# Copyright 2015 iDT LABS (http://www.@idtlabs.sl)
# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrHolidaysStatus(models.Model):
    _inherit = 'hr.holidays.status'

    exclude_public_holidays = fields.Boolean(
        string='Exclude Public Holidays',
        default=True,
        help="If enabled, public holidays are skipped in leave days "
             "calculation.",
    )
