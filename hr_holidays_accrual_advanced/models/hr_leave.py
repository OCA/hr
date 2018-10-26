# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    time_type = fields.Selection(
        related='holiday_status_id.time_type',
        store=True,
    )
    unpaid = fields.Boolean(
        related='holiday_status_id.unpaid',
        store=True,
    )
