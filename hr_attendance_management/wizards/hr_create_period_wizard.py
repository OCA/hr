# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api


class ChangeDayDWizard(models.TransientModel):
    _name = 'hr.create.period.wizard'

    employee_id = fields.Many2one('hr.employee', string="ID of concerned employee",
                                  compute="_compute_employee_id")
    start_date = fields.Date(string="Start date of new period")
    end_date = fields.Date(string="End date of new period")
    continuous_cap = fields.Boolean(string="Employee capped or not",
                                    related="employee_id.extra_hours_continuous_cap")

    def _compute_employee_id(self):
        active_ids = self.env.context.get('active_ids')
        employee_records = self.env['hr.employee'].browse(active_ids)
        for employee in employee_records:
            self.employee_id = employee

    def create_period(self):
        for record in self:
            if not record.employee_id:
                record._compute_employee_id()
            previous_periods = record.employee_id.period_ids.filtered(
                lambda r: r.end_date <= record.start_date
            ).sorted(key=lambda r: r.start_date)
            previous_period_id = 0
            if previous_periods:
                previous_period_id = previous_periods[-1].id

            record.employee_id.create_period(record.employee_id.id,
                                             record.start_date,
                                             # Add one day to end_date as the logic uses an exclusive superior bound
                                             str(datetime.datetime.strptime(record.end_date, '%Y-%m-%d').date()
                                                 + datetime.timedelta(days=1)),
                                             0,
                                             previous_period_id,
                                             0,
                                             record.continuous_cap)
