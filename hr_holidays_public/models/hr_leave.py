# Copyright 2017-2021 Tecnativa - Pedro M. Baeza
# Copyright 2018 Brainbean Apps
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    def _get_number_of_days(self, date_from, date_to, employee_id):
        if (self.holiday_status_id.exclude_public_holidays or
                not self.holiday_status_id):
            instance = self.with_context(
                employee_id=employee_id,
                exclude_public_holidays=True,
            )
        else:
            instance = self
        return super(HrLeave, instance)._get_number_of_days(
            date_from,
            date_to,
            employee_id,
        )

    @api.multi
    @api.depends("date_from", "date_to")
    def _compute_number_of_hours_display(self):
        for holiday in self:

            super(HrLeave, holiday)._compute_number_of_hours_display()

            if holiday.date_from and holiday.date_to:
                date_from = holiday.date_from
                date_to = holiday.date_to
                calendar = holiday.employee_id.sudo(
                ).resource_calendar_id or self.env.user.company_id.resource_calendar_id

                if holiday.holiday_status_id.exclude_public_holidays:
                    number_of_hours = calendar.with_context(
                        exclude_public_holidays=True,
                        employee_id=holiday.employee_id.id).get_work_hours_count(
                        date_from, date_to
                    )
                else:
                    # Even if we do not exclude public holidays,
                    # we should use employee's work calendar
                    # to compute the number of hours
                    number_of_hours = calendar.with_context(
                        employee_id=holiday.employee_id.id).get_work_hours_count(
                        date_from, date_to)

                holiday.number_of_hours_display = number_of_hours

            else:
                holiday.number_of_hours_display = 0
