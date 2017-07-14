# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class HrHolidaysStatus(models.Model):
    _inherit = "hr.holidays.status"

    @api.multi
    def get_hours(self, employee):
        self.ensure_one()
        result = {
            'max_hours': 0,
            'remaining_hours': 0,
            'hours_taken': 0,
            'virtual_remaining_hours': 0,
        }

        holiday_ids = employee.holiday_ids.filtered(
            lambda x: x.state in [
                'confirm',
                'validate1',
                'validate'
            ] and x.holiday_status_id == self)

        for holiday in holiday_ids:
            hours = holiday.number_of_hours_temp
            if holiday.type == 'add':
                result['virtual_remaining_hours'] += hours
                if holiday.state == 'validate':
                    result['max_hours'] += hours
                    result['remaining_hours'] += hours
            elif holiday.type == 'remove':  # number of days is negative
                result['virtual_remaining_hours'] -= hours
                if holiday.state == 'validate':
                    result['hours_taken'] += hours
                    result['remaining_hours'] -= hours

        return result

    @api.multi
    def _compute_user_left_hours(self):
        employee_id = self._context.get('employee_id', False)
        employee = None
        if not employee_id:
            employees = self.env.user.employee_ids
            if employees:
                employee = employees[0]
        else:
            employee = self.env['hr.employee'].browse(employee_id)

        for status in self:
            status.hours_taken = 0
            status.remaining_hours = 0
            status.max_hours = 0
            status.virtual_remaining_hours = 0
            if employee:
                res = status.get_hours(employee)
                status.hours_taken = res['hours_taken']
                status.remaining_hours = res['remaining_hours']
                status.max_hours = res['max_hours']
                status.virtual_remaining_hours = res[
                    'virtual_remaining_hours'
                ]

    max_hours = fields.Float(
        compute="_compute_user_left_hours",
        string='Maximum Allowed Hours'
    )
    hours_taken = fields.Float(
        compute="_compute_user_left_hours",
        string='Hours Already Taken'
    )
    remaining_hours = fields.Float(
        compute="_compute_user_left_hours"
    )
    virtual_remaining_hours = fields.Float(
        compute="_compute_user_left_hours"
    )

    @api.multi
    def name_get(self):
        if not self._context.get('employee_id', False):
            # leave counts is based on employee_id, would be
            # inaccurate if not based on correct employee
            return super(HrHolidaysStatus, self).name_get()

        res = []
        for record in self:
            name = record.name
            if not record.limit:
                name += ('  (%.1f Left)' % (record.remaining_hours))
            res.append((record.id, name))
        return res
