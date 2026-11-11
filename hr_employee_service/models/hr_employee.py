# Copyright (C) 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta
from math import fabs

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    service_hire_date = fields.Date(
        string="Hire Date",
        groups="hr.group_hr_user",
        tracking=True,
        help=(
            "Hire date is normally the date an employee completes new hire paperwork"
        ),
    )
    service_start_date = fields.Date(
        string="Start Date",
        groups="hr.group_hr_user",
        tracking=True,
        help=(
            "Start date is the first day the employee actually works and"
            " this date is used for accrual leave allocations calculation"
        ),
    )
    service_termination_date = fields.Date(
        string="Termination Date",
        related="departure_date",
        help=(
            "Termination date is the last day the employee actually works and"
            " this date is used for accrual leave allocations calculation"
        ),
    )
    service_duration = fields.Integer(
        groups="hr.group_hr_user",
        readonly=True,
        compute="_compute_service_duration",
        help="Service duration in days",
    )
    service_duration_years = fields.Integer(
        string="Service Duration (years)",
        groups="hr.group_hr_user",
        readonly=True,
        compute="_compute_service_duration_display",
    )
    service_duration_months = fields.Integer(
        string="Service Duration (months)",
        groups="hr.group_hr_user",
        readonly=True,
        compute="_compute_service_duration_display",
    )
    service_duration_days = fields.Integer(
        string="Service Duration (days)",
        groups="hr.group_hr_user",
        readonly=True,
        compute="_compute_service_duration_display",
    )

    @api.depends("service_start_date", "service_termination_date")
    def _compute_service_duration(self):
        for record in self:
            service_until = record.service_termination_date or fields.Date.today()
            if record.service_start_date and service_until > record.service_start_date:
                service_since = record.service_start_date
                service_duration = fabs(
                    (service_until - service_since) / timedelta(days=1)
                )
                record.service_duration = int(service_duration)
            else:
                record.service_duration = 0

    @api.depends("service_start_date", "service_termination_date")
    def _compute_service_duration_display(self):
        for record in self:
            service_until = record.service_termination_date or fields.Date.today()
            if record.service_start_date and service_until > record.service_start_date:
                service_duration = relativedelta(
                    service_until, record.service_start_date
                )
                record.service_duration_years = service_duration.years
                record.service_duration_months = service_duration.months
                record.service_duration_days = service_duration.days
            else:
                record.service_duration_years = 0
                record.service_duration_months = 0
                record.service_duration_days = 0

    @api.onchange("service_hire_date")
    def _onchange_service_hire_date(self):
        if not self.service_start_date:
            self.service_start_date = self.service_hire_date

    def get_service_duration_from_date(self, date=None):
        """
        Returns the employee service duration for the given date.
        This function is used in OCA/payroll modules as a helper function
        to calculate employee service duration calculated for the given date.
        """
        self.ensure_one()
        if not date or not self.service_start_date:
            return {"years": 0, "months": 0, "days": 0}
        if date > self.service_start_date:
            service_duration = relativedelta(date, self.service_start_date)
            return {
                "years": service_duration.years,
                "months": service_duration.months,
                "days": service_duration.days,
            }
        return {"years": 0, "months": 0, "days": 0}
