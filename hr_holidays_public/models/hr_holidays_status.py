# Copyright 2015 iDT LABS (http://www.@idtlabs.sl)
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrHolidaysStatus(models.Model):
    _inherit = 'hr.holidays.status'

    exclude_rest_days = fields.Boolean(
        string='Exclude Rest Days',
        default=True,
        help="If enabled, the employee's day off is skipped in leave days "
             "calculation.",
    )
    exclude_public_holidays = fields.Boolean(
        string='Exclude Public Holidays',
        default=True,
        help="If enabled, public holidays are skipped in leave days "
        "calculation.",
    )
    compute_full_days = fields.Boolean(
        string="Compute Full Days",
        default=True,
        help="If enabled, the number of days computed will be always for the "
             "full days in the interval",
    )
