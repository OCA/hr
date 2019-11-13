# -*- coding: utf-8 -*-
# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class WizardEmployeeCalendarDates(models.TransientModel):
    _name = 'wizard.employee.calendar.dates'
    _description = 'Assign calendar for a date range to employees'

    employee_ids = fields.Many2many(
        comodel_name='hr.employee',
        required=True,
        string='Employees',
        help='Assign to these employees',
    )
    calendar_id = fields.Many2one(
        comodel_name='resource.calendar',
        required=True,
        string='Calendar',
        help='Assign this calendar',
    )
    date_start = fields.Date(
        string='From',
    )
    date_end = fields.Date(
        string='To',
    )

    @api.multi
    def action_assign_calendar(self):
        self.ensure_one()
        employee_cal_obj = self.env['hr.employee.calendar']
        for employee in self.employee_ids:
            employee_cal_obj.create({
                'employee_id': employee.id,
                'calendar_id': self.calendar_id.id,
                'date_start': self.date_start,
                'date_end': self.date_end,
            })
        return
