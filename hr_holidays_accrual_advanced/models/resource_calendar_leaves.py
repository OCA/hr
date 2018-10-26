# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResourceCalendarLeaves(models.Model):
    _inherit = 'resource.calendar.leaves'

    holiday_status_id = fields.Many2one(
        related='holiday_id.holiday_status_id',
        store=True,
    )
    unpaid = fields.Boolean(
        related='holiday_id.holiday_status_id.unpaid',
        store=True,
    )
