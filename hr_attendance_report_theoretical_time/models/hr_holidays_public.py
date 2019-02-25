# Copyright 2017-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from datetime import datetime, time


class HrHolidaysPublicLine(models.Model):
    _inherit = 'hr.holidays.public.line'

    @api.model
    def _check_theoretical_hours(self, date):
        """Recomputes all the theoretical hours that corresponds to the date
        of the public holiday.

        :param: date: Date for recomputing attendances.
        """
        if not date:
            return
        if isinstance(date, str):
            date = fields.Date.from_string(date)
        from_datetime = datetime.combine(date, time(0, 0, 0, 0))
        to_datetime = datetime.combine(date, time(23, 59, 59, 99999))
        records = self.env['hr.attendance'].search([
            ('check_in', '>=', fields.Datetime.to_string(from_datetime)),
            ('check_in', '<=', fields.Datetime.to_string(to_datetime)),
        ])
        records._compute_theoretical_hours()

    @api.model
    def create(self, vals_list):
        """Trigger recomputation for the date of the new lines."""
        records = super(HrHolidaysPublicLine, self).create(vals_list)
        for record in records:
            self._check_theoretical_hours(record.date)
        return records

    def write(self, vals):
        """If the date of a line is changed, we first recompute hours of the
        previous date, and then the theoretical hours of the current date.
        """
        if 'date' in vals:
            dates = set(self.mapped('date'))
            dates.add(vals['date'])
        res = super(HrHolidaysPublicLine, self).write(vals)
        if 'date' in vals:
            for date in dates:
                self._check_theoretical_hours(date=date)
        return res
