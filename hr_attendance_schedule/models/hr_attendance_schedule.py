# -*- coding: utf-8 -*-
from odoo import fields, models


class Schedule(models.Model):
    _name = 'hr_attendance_schedule.schedule'

    employee_ids = fields.One2many('hr.employee', 'schedule_id', "Employees")
    period_ids = fields.One2many('hr_attendance_schedule.period', 'schedule_id', "Periods")
    active = fields.Boolean(default=True)
    name = fields.Char(required=True)

    def get_action_date(self, in_out):
        results = (p.get_action_date(in_out) for p in self.period_ids)
        return next(((d, a) for d, a in results if d is not None), (fields.Datetime.now(), True))
