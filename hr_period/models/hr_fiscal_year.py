# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from datetime import datetime
strftime = datetime.strptime
from dateutil.relativedelta import relativedelta

from openerp import models, fields, api,  _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.exceptions import Warning as UserError


INTERVALS = {
    'annually': (relativedelta(months=12), 1),
    'semi-annually': (relativedelta(months=6), 2),
    'quaterly': (relativedelta(months=3), 4),
    'bi-monthly': (relativedelta(months=2), 6),
    'monthly': (relativedelta(months=1), 12),
    'bi-weekly': (relativedelta(weeks=2), 26),
    'weekly': (relativedelta(weeks=1), 52),
    'daily': (relativedelta(days=1), 365),
}


@api.model
def get_schedules(self):
    return [
        ('annually', _('Annually (1)')),
        ('semi-annually', _('Semi-annually (2)')),
        ('quarterly', _('Quarterly (4)')),
        ('bi-monthly', _('Bi-monthly (6)')),
        ('monthly', _('Monthly (12)')),
        ('semi-monthly', _('Semi-monthly (24)')),
        ('bi-weekly', _('Bi-weekly (26)')),
        ('weekly', _('Weekly (52)')),
        ('daily', _('Daily (365)')),
    ]


@api.model
def get_payment_days(self):
    expr = _('%s day of the next period')
    expr_2 = _('%s day of the current period')
    return [
        ('1', expr % _('First')),
        ('2', expr % _('Second')),
        ('3', expr % _('Third')),
        ('4', expr % _('Fourth')),
        ('5', expr % _('Fifth')),
        ('0', expr_2 % _('Last')),
    ]


class HrFiscalYear(models.Model):
    _name = 'hr.fiscalyear'
    _description = 'HR Fiscal Year'

    @api.model
    def _default_date_start(self):
        today = datetime.now()
        return datetime(today.year, 1, 1).strftime(
            DEFAULT_SERVER_DATE_FORMAT)

    @api.model
    def _default_date_stop(self):
        today = datetime.now()
        return datetime(today.year, 12, 31).strftime(
            DEFAULT_SERVER_DATE_FORMAT)

    name = fields.Char(
        'Fiscal Year',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda obj: obj.env.user.company_id
    )
    date_start = fields.Date(
        'Start Date',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="The first day of the first period of the "
        "fiscal year.",
        default=_default_date_start
    )
    date_stop = fields.Date(
        'End Date',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="The last day of the last period of the "
        "fiscal year.",
        default=_default_date_stop
    )
    period_ids = fields.One2many(
        'hr.period',
        'fiscalyear_id',
        'Periods',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('open', 'Open'),
            ('done', 'Closed'),
        ],
        'Status',
        readonly=True,
        default='draft'
    )
    schedule_pay = fields.Selection(
        get_schedules,
        'Scheduled Pay',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default='monthly'
    )
    payment_weekday = fields.Selection(
        [
            ('0', 'Sunday'),
            ('1', 'Monday'),
            ('2', 'Tuesday'),
            ('3', 'Wednesday'),
            ('4', 'Thursday'),
            ('5', 'Friday'),
            ('6', 'Saturday'),
        ], 'Day of Payment',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    payment_week = fields.Selection(
        [
            ('0', 'Same Week'),
            ('1', 'Following Week'),
            ('2', 'Second Following Week'),
        ], 'Week of Payment',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    payment_day = fields.Selection(
        get_payment_days,
        'Day of Payment',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    @api.onchange('schedule_pay', 'date_start')
    @api.multi
    def onchange_schedule(self):
        if self.schedule_pay and self.date_start:
            year = datetime.strptime(
                self.date_start, DEFAULT_SERVER_DATE_FORMAT).year

            schedule_name = next((
                s[1] for s in get_schedules(self)
                if s[0] == self.schedule_pay), False)

            self.name = '%(year)s - %(schedule)s' % {
                'year': year,
                'schedule': schedule_name,
            }

    @api.one
    def create_periods(self):
        """
        Create every periods a payroll fiscal year
        """
        for period in self.period_ids:
            period.unlink()

        self.refresh()

        period_start = datetime.strptime(
            self.date_start, DEFAULT_SERVER_DATE_FORMAT)

        next_year_start = datetime.strptime(
            self.date_stop,
            DEFAULT_SERVER_DATE_FORMAT) + relativedelta(days=1)

        if self.schedule_pay == 'semi-monthly':
            #  Case for semi-monthly schedules
            delta_1 = relativedelta(days=15)
            delta_2 = relativedelta(months=1)

            i = 1
            while not period_start + delta_2 > next_year_start:
                # create periods for one month
                half_month = period_start + delta_1
                self._create_single_period(period_start, half_month, i)
                self._create_single_period(
                    half_month, period_start + delta_2, i + 1)

                # setup for next month
                period_start += delta_2
                i += 2
        else:  # All other cases
            delta, nb_periods = INTERVALS[self.schedule_pay]

            i = 1
            while not period_start + delta > next_year_start:
                self._create_single_period(
                    period_start, period_start + delta, i)
                period_start += delta
                i += 1

    @api.multi
    def _create_single_period(self, date_start, date_stop, number):
        """ Create a single payroll period
        :param date_start: the first day of the actual period
        :param date_stop: the first day of the following period
        """
        self.ensure_one()

        date_stop -= relativedelta(days=1)

        self.write({
            'period_ids': [(0, 0, {
                'date_start': date_start,
                'date_stop': date_stop,
                'date_payment': self._get_day_of_payment(date_stop),
                'company_id': self.company_id.id,
                'name': _('%s Period #%s') % (self.name, number),
                'number': number,
                'state': 'draft',
                'schedule_pay': self.schedule_pay,
            })],
        })

    @api.multi
    def _get_day_of_payment(self, date_stop):
        """
        Get the date of payment for a period to create
        :param date_stop: the last day of the current period
        """
        self.ensure_one()

        date_payment = date_stop
        if self.schedule_pay in ['weekly', 'bi-weekly']:
            date_payment += relativedelta(weeks=int(self.payment_week))
            while date_payment.strftime('%w') != self.payment_weekday:
                date_payment -= relativedelta(days=1)
        else:
            date_payment += relativedelta(days=int(self.payment_day))
        return date_payment

    @api.multi
    def button_confirm(self):
        for fy in self:
            if not fy.period_ids:
                raise UserError(_('You must create periods before confirming '
                                  'the fiscal year.'))
        self.state = 'open'
        for fy in self:
            first_period = fy.period_ids.sorted(key=lambda p: p.number)[0]
            first_period.button_open()

    @api.multi
    def button_set_to_draft(self):
        # Set all periods to draft
        periods = self.mapped('period_ids')
        periods.button_set_to_draft()
        self.state = 'draft'

    @api.multi
    def search_period(self, number):
        return next((p for p in self.period_ids if p.number == number),
                    self.env['hr.period'])
