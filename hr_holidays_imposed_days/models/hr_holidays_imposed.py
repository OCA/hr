# Author: Damien Crier
# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
import math

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError

HOURS_PER_DAY = 8


class HrHolidaysImposed(models.Model):
    _name = 'hr.holidays.imposed'
    _description = 'Manage imposed holidays'

    name = fields.Char(required=True)
    date_from = fields.Datetime(required=True)
    date_to = fields.Datetime(required=True)
    number_of_days = fields.Float()
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env['res.company']._company_default_get(
            'hr.holidays.imposed')
    )
    status_id = fields.Many2one(
        'hr.holidays.status',
        string="Leave type",
        required=True
    )
    employee_ids = fields.Many2many(
        'hr.employee',
        help="If empty, all employees of the "
             "company will have this day/period "
             "imposed")
    auto_confirm = fields.Boolean()

    @api.multi
    def validate(self):
        for rec in self:
            created = self.env['hr.holidays']
            if rec.employee_ids:
                employees = rec.employee_ids
            else:
                employees = self.env['hr.employee'].search([
                    ('company_id', '=', rec.company_id.id)
                ])
            for employee in employees:
                vals = rec._prepare_leave_from_imposed_day()
                vals.update({'employee_id': employee.id})
                leave = self.env['hr.holidays'].create(vals)
                leave._onchange_date_from()
                created |= leave
            if rec.auto_confirm:
                created.action_validate()

    @api.model
    def _get_duration(self):
        """Returns a float equals to the timedelta between
           two dates given as string."""

        self.ensure_one()
        from_dt = fields.Datetime.from_string(self.date_from)
        to_dt = fields.Datetime.from_string(self.date_to)
        timedelta = to_dt - from_dt
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
        return diff_day

    @api.multi
    def _set_duration(self):
        """Computes and updates the number of days"""
        self.ensure_one()
        if (self.date_to and self.date_from and
                self.date_from <= self.date_to):
            diff_day = self._get_duration()
            self.number_of_days = self.compute_nb_days(diff_day)
        else:
            self.number_of_days = 0

    @api.onchange('date_from', 'date_to')
    def onchange_dates(self):
        """
        If there are no date set for date_to, automatically set one
        HOURS_PER_DAY later than the date_from.
        Also update the number_of_days.
        """
        # Because when setting date_from, date_to is set to actual day and
        # will trigger an error.
        if not self.id and self.date_from and \
           self.date_to is False or self.date_from > self.date_to:
            date_to_with_delta = datetime.datetime.strptime(
                self.date_from,
                tools.DEFAULT_SERVER_DATETIME_FORMAT) + datetime.timedelta(
                hours=HOURS_PER_DAY)
            self.date_to = str(date_to_with_delta)

        # date_to has to be greater than date_from
        self._check_dates()

        # No date_to set so far: automatically compute one HOURS_PER_DAY later
        if self.date_from and not self.date_to:
            date_to_with_delta = datetime.datetime.strptime(
                self.date_from,
                tools.DEFAULT_SERVER_DATETIME_FORMAT) + datetime.timedelta(
                hours=HOURS_PER_DAY)
            self.date_to = str(date_to_with_delta)

        # Compute and update the number of days
        self._set_duration()

    @classmethod
    def compute_nb_days(self, diff):
        return round(math.floor(diff)) + 1

    @api.multi
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if (record.date_from and record.date_to and
                    record.date_from > record.date_to):
                raise ValidationError(
                    _('The start date must be anterior to the end date.'))

    @api.multi
    def _prepare_leave_from_imposed_day(self):
        self.ensure_one()
        values = {
            'number_of_days_temp': self.number_of_days,
            'name': self.name,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'type': 'remove',
            'holiday_status_id': self.status_id.id,
        }
        return values
