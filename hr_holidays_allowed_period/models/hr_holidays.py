# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class HrHolidays(models.Model):

    _inherit = 'hr.holidays'

    warning = fields.Char(compute='_compute_warning_range')

    @api.depends('holiday_status_id', 'date_from', 'date_to')
    def _compute_warning_range(self):
        if self.type == 'remove' and self.holiday_status_id and \
                self.holiday_status_id.period_from and \
                self.holiday_status_id.period_to:
            if self.date_from and self.date_to:
                int_from = fields.Datetime.to_string(
                    fields.Date.from_string(self.holiday_status_id.period_from)
                )
                int_to = fields.Datetime.to_string(
                    fields.Date.from_string(self.holiday_status_id.period_to)
                )
                if self.date_from < int_from or self.date_to > int_to:
                    self.warning = _(
                        'Warning: The selected dates '
                        'are out of this holiday type\'s '
                        'range. (%s - %s)') % (
                        self.holiday_status_id.period_from,
                        self.holiday_status_id.period_to)
                    return
        self.warning = False
