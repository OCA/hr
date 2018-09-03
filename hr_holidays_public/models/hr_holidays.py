# Copyright 2015 iDT LABS (http://www.@idtlabs.sl)
# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    def _get_number_of_days(self, date_from, date_to, employee_id):
        if (self.holiday_status_id.exclude_public_holidays or
                not self.holiday_status_id):
            obj = self.with_context(
                employee_id=employee_id,
                exclude_public_holidays=True,
            )
        else:
            obj = self
        return super(HrHolidays, obj)._get_number_of_days(
            date_from, date_to, employee_id,
        )

    @api.onchange('employee_id', 'holiday_status_id')
    def _onchange_data_hr_holidays_public(self):
        """Trigger the number of days computation also when you change the
        employee or the leave type.
        """
        self._onchange_date_to()
