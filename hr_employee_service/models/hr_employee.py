# Copyright (C) 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api

from math import fabs
from dateutil.relativedelta import relativedelta
from datetime import timedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    service_hire_date = fields.Date(
        string='Hire Date',
        groups='hr.group_hr_user',
        track_visibility='onchange',
        help=(
            'Hire date is normally the date an employee completes new hire'
            ' paperwork'
        ),
    )
    service_start_date = fields.Date(
        string='Start Date',
        groups='hr.group_hr_user',
        track_visibility='onchange',
        help=(
            'Start date is the first day the employee actually works and'
            ' this date is used for accrual leave allocations calculation'
        ),
    )
    service_termination_date = fields.Date(
        string='Termination Date',
        groups='hr.group_hr_user',
        track_visibility='onchange',
        help=(
            'Termination date is the last day the employee actually works and'
            ' this date is used for accrual leave allocations calculation'
        ),
    )
    service_duration = fields.Integer(
        string='Service Duration',
        groups='hr.group_hr_user',
        readonly=True,
        compute='_compute_service_duration',
        help='Service duration in days',
    )
    service_duration_years = fields.Integer(
        string='Service Duration (years)',
        groups='hr.group_hr_user',
        readonly=True,
        compute='_compute_service_duration_display',
    )
    service_duration_months = fields.Integer(
        string='Service Duration (months)',
        groups='hr.group_hr_user',
        readonly=True,
        compute='_compute_service_duration_display',
    )
    service_duration_days = fields.Integer(
        string='Service Duration (days)',
        groups='hr.group_hr_user',
        readonly=True,
        compute='_compute_service_duration_display',
    )

    @api.multi
    @api.depends('service_start_date', 'service_termination_date')
    def _compute_service_duration(self):
        for record in self:
            service_until = (
                record.service_termination_date or fields.Date.today()
            )
            if record.service_start_date and \
                    service_until > record.service_start_date:
                service_since = record.service_start_date
                service_duration = fabs(
                    (service_until - service_since) / timedelta(days=1)
                )
                record.service_duration = int(service_duration)
            else:
                record.service_duration = 0

    @api.multi
    @api.depends('service_start_date', 'service_termination_date')
    def _compute_service_duration_display(self):
        for record in self:
            service_until = (
                record.service_termination_date or fields.Date.today()
            )
            if record.service_start_date and \
                    service_until > record.service_start_date:
                service_duration = relativedelta(
                    service_until,
                    record.service_start_date
                )
                record.service_duration_years = service_duration.years
                record.service_duration_months = service_duration.months
                record.service_duration_days = service_duration.days
            else:
                record.service_duration_years = 0
                record.service_duration_months = 0
                record.service_duration_days = 0

    @api.multi
    @api.onchange('service_hire_date')
    def _onchange_service_hire_date(self):
        if not self.service_start_date:
            self.service_start_date = self.service_hire_date

    # NOTE: Support odoo/odoo@90731ad170c503cdfe89a9998fa1d1e2a5035c86
    def _get_date_start_work(self):
        return self.service_start_date or super()._get_date_start_work()
