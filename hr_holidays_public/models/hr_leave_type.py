# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# Copyright 2018 Brainbean Apps
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    exclude_public_holidays = fields.Boolean(
        string='Exclude Public Holidays',
        default=True,
        help=(
            'If enabled, public holidays are skipped in leave days'
            ' calculation.'
        ),
    )
