# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api


class ChangeDayDWizard(models.TransientModel):
    _name = 'hr.create.period.wizard'

    employee_id = fields.Many2one('hr.employee', string="ID of concerned employee")
    start_date = fields.Date(string="Start date of new period")
    end_date = fields.Date(string="End date of new period")
    continuous_cap = fields.Boolean(string="Employee capped or not")

    def create_period(self):
        for record in self:
            active_ids = self.env.context.get('active_ids')
            employee_records = self.env['hr.employee'].browse(active_ids)
            for employee in employee_records:
                employee.create_period(employee.id,
                                       record.start_date,
                                       record.end_date,
                                       0,
                                       0,
                                       0,
                                       record.continuous_cap)


