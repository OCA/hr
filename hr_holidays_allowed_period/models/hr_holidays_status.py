# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrHolidaysStatus(models.Model):

    _inherit = 'hr.holidays.status'

    period_from = fields.Date(string='Date from')
    period_to = fields.Date(string='Date to')
