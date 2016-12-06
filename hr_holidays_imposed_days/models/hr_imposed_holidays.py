# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
import math

from openerp import models, fields, api, exceptions, _
from openerp import tools


class HrHolidaysImposed(models.Model):
    _name = 'hr.holidays.imposed'
    _description = 'Manage imposed holidays'

    name = fields.Char(required=True)
    date_from = fields.Datetime(required=True)
    date_to = fields.Datetime(required=True)
    number_of_days = fields.Float()
    company_id = fields.Many2one(
        comodel_name='res.company',
        string="Company",
        default=lambda self: self.env['res.company']._company_default_get(
            'hr.holidays.imposed')
    )
    status_id = fields.Many2one(
        comodel_name='hr.holidays.status',
        string="Leave type",
        required=True
    )
    employee_ids = fields.Many2many(comodel_name='hr.employee',
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
                employees = self.env['hr.employee'].search(
                    [('company_id', '=', rec.company_id.id)])

            for employee in employees:
                vals = {
                    'name': rec.name,
                    'date_from': rec.date_from,
                    'date_to': rec.date_to,
                    'employee_id': employee.id,
                    'type': 'remove',
                    'holiday_status_id': rec.status_id.id,
                }
                leave = created.create(vals)
                res = leave.onchange_date_from(rec.date_to, rec.date_from,)
                leave.write(res['value'])
                created |= leave
            if rec.auto_confirm:
                created.signal_workflow('validate')

    def _get_number_of_days(self, date_from, date_to):
        """Returns a float equals to the timedelta between
           two dates given as string."""

        from_dt = fields.Datetime.from_string(date_from)
        to_dt = fields.Datetime.from_string(date_to)
        timedelta = to_dt - from_dt
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
        return diff_day

    @api.onchange('date_from', 'date_to')
    def onchange_dates(self):
        """
        If there are no date set for date_to, automatically set one
        8 hours later than the date_from.
        Also update the number_of_days.
        """
        # date_to has to be greater than date_from
        if ((self.date_from and self.date_to) and
                (self.date_from > self.date_to)):
            raise exceptions.Warning(
                _('The start date must be anterior to the end date.'))

        # No date_to set so far: automatically compute one 8 hours later
        if self.date_from and not self.date_to:
            date_to_with_delta = datetime.datetime.strptime(
                self.date_from,
                tools.DEFAULT_SERVER_DATETIME_FORMAT) + datetime.timedelta(
                hours=8)
            self.date_to = str(date_to_with_delta)

        # Compute and update the number of days
        if ((self.date_to and self.date_from) and
                (self.date_from <= self.date_to)):
            diff_day = self._get_number_of_days(self.date_from, self.date_to)
            self.number_of_days = self.compute_nb_days(diff_day)
        else:
            self.number_of_days = 0

    def compute_nb_days(self, diff):
        return round(math.floor(diff))+1
