# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    active = fields.Boolean(
        default=True,
    )
