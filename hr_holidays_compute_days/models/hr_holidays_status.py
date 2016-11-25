# -*- coding: utf-8 -*-
# ©  2015 iDT LABS (http://www.@idtlabs.sl)
# © 2016 MONK Software (http://www.wearemonk.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class HrHolidaysStatus(models.Model):
    _inherit = 'hr.holidays.status'

    exclude_rest_days = fields.Boolean(
        'Exclude Rest Days',
        help="If enabled, the employee's day off is skipped in leave days "
             "calculation.",
    )
    exclude_public_holidays = fields.Boolean(
        'Exclude Public Holidays',
        help="If enabled, public holidays are skipped in leave days "
        "calculation.",
    )
    allow_partial_days = fields.Boolean(
        'Allow Partial Days',
        help="If enabled, compute float days.")
    allow_boundaries_nonworking_days = fields.Boolean(
        'Allow start/end on non-working days',
        help=('If enabled, employees can schedule leaves of this type that'
              'start and/or end on non-working days'))
