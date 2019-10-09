# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrHolidaysPublicLine(models.Model):
    _inherit = 'hr.holidays.public.line'

    def _check_theoretical_hours(self, date=None):
        """Recomputes all the theoretical hours that corresponds to the date
        of the public holiday.

        :param: date: (Optional) Specific date for recomputing attendances.
        """
        self.ensure_one()
        dt = date or self.date
        if not dt:
            return
        dt = fields.Datetime.from_string(dt)
        from_datetime = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        to_datetime = dt.replace(
            hour=23, minute=59, second=59, microsecond=99999,
        )
        records = self.env['hr.attendance'].search([
            ('check_in', '>=', fields.Datetime.to_string(from_datetime)),
            ('check_in', '<=', fields.Datetime.to_string(to_datetime)),
        ])
        records._compute_theoretical_hours()

    def create(self, vals):
        """Trigger recomputation for the date of the new line."""
        record = super(HrHolidaysPublicLine, self).create(vals)
        record._check_theoretical_hours()
        return record

    def write(self, vals):
        """If the date of a line is changed, we first recompute hours of the
        previous date, and then the theoretical hours of the current date.
        """
        if 'date' in vals:
            dates = {x: x.date for x in self}
        res = super(HrHolidaysPublicLine, self).write(vals)
        if 'date' in vals:
            for record in dates:
                record._check_theoretical_hours(date=dates[record])
            self._check_theoretical_hours(date=vals['date'])
        return res
