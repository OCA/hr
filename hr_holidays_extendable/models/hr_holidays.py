# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrHolidays(models.Model):

    _inherit = 'hr.holidays'

    extendable = fields.Boolean(
        related='holiday_status_id.extendable',
        store=True,
        readonly=True,
    )
