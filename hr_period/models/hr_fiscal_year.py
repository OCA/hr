# Copyright 2015 Savoir-faire Linux. All Rights Reserved.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from dateutil.rrule import (YEARLY,
                            MONTHLY,
                            WEEKLY,
                            DAILY)
from datetime import datetime

strptime = datetime.strptime
strftime = datetime.strftime

INTERVALS = {
    'annually': (relativedelta(months=12), 1),
    'semi-annually': (relativedelta(months=6), 2),
    'quarterly': (relativedelta(months=3), 4),
    'bi-monthly': (relativedelta(months=2), 6),
    'semi-monthly': (relativedelta(weeks=2), 24),
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
    _inherit = 'date.range'
    _description = 'HR Fiscal Year'

    @api.model
    def _default_date_start(self):
        today = datetime.now()
        return datetime(today.year, 1, 1).strftime(DF)

    @api.model
    def _default_date_end(self):
        today = datetime.now()
        return datetime(today.year, 12, 31).strftime(DF)

    @api.model
    def _default_type(self, company_id=False):
        if not company_id:
            company_id = self.env.user.company_id.id
        period_type = self.env['date.range.type'].search(
            [('hr_fiscal_year', '=', True),
             ('company_id', '=', company_id)], limit=1)
        return period_type

    period_ids = fields.One2many(
        'hr.period',
        'fiscalyear_id',
        'Periods',
        states={'draft': [('readonly', False)]}
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('open', 'Open'),
            ('done', 'Closed'),
        ],
        'Status',
        default='draft'
    )
    schedule_pay = fields.Selection(
        get_schedules,
        'Scheduled Pay',
        required=True,
        states={'draft': [('readonly', False)]},
        default='monthly'
    )
    type_id = fields.Many2one(
        domain=[('hr_fiscal_year', '=', True)],
        default=_default_type
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
        ], 'Weekday of Payment',
        states={'draft': [('readonly', False)]}
    )
    payment_week = fields.Selection(
        [
            ('0', 'Same Week'),
            ('1', 'Following Week'),
            ('2', 'Second Following Week'),
        ], 'Week of Payment',
        states={'draft': [('readonly', False)]}
    )
    payment_day = fields.Selection(
        get_payment_days,
        'Day of Payment',
        states={'draft': [('readonly', False)]}
    )

    @api.multi
    def _count_range_no(self):
        days_range = abs((strptime(str(self.date_end), DF) -
                          strptime(str(self.date_start), DF)).days) + 1
        return INTERVALS[self.schedule_pay][1] * days_range / 365

    @api.multi
    @api.onchange('schedule_pay', 'date_start')
    def onchange_schedule(self):
        if self.schedule_pay and self.date_start:
            year = datetime.strptime(str(self.date_start), DF).year
            schedule_name = next((
                s[1] for s in get_schedules(self)
                if s[0] == self.schedule_pay), False)
            self.name = '%(year)s - %(schedule)s' % {
                'year': year,
                'schedule': schedule_name,
            }

    @api.model
    def get_generator_vals(self):
        no_interval = 1
        if self.schedule_pay == 'daily':
            unit_of_time = DAILY
        elif self.schedule_pay == 'weekly':
            unit_of_time = WEEKLY
        elif self.schedule_pay == 'bi-weekly':
            unit_of_time = WEEKLY
            no_interval = 2
        elif self.schedule_pay == 'monthly':
            unit_of_time = MONTHLY
        elif self.schedule_pay == 'bi-monthly':
            unit_of_time = MONTHLY
            no_interval = 2
        elif self.schedule_pay == 'quarterly':
            unit_of_time = MONTHLY
            no_interval = 4
        elif self.schedule_pay == 'semi-annually':
            unit_of_time = MONTHLY
            no_interval = 6
        else:
            unit_of_time = YEARLY
        return {
            'name_prefix': self.name,
            'date_start': self.date_start,
            'type_id': self.type_id.id,
            'company_id': self.company_id.id,
            'unit_of_time': unit_of_time,
            'duration_count': no_interval,
            'count': self._count_range_no()
        }

    @api.multi
    def get_ranges(self):
        self.ensure_one()
        vals = self.get_generator_vals()
        range_generator = self.env['date.range.generator'].create(vals)
        date_ranges = range_generator._compute_date_ranges()
        return date_ranges

    @api.multi
    def create_periods(self):
        """
        Create every periods a payroll fiscal year
        """
        for fy in self:
            for period in fy.period_ids:
                period.unlink()
            fy.refresh()
        if self.date_start > self.date_end:
            raise UserError(_('''Date stop cannot be sooner than the date start
                                '''))
        if self.schedule_pay == 'semi-monthly':
            period_start = datetime.strptime(
                str(self.date_start), DF)
            next_year_start = datetime.strptime(
                str(self.date_end), DF) + relativedelta(days=1)
            #  Case for semi-monthly schedules
            delta_1 = relativedelta(days=14)
            delta_2 = relativedelta(months=1)
            i = 1
            while not period_start + delta_2 > next_year_start:
                # create periods for one month
                half_month = period_start + delta_1
                self._create_single_period(period_start, half_month, i)
                self._create_single_period(
                    half_month + relativedelta(days=1),
                    period_start + delta_2 - relativedelta(days=1), i + 1)
                # setup for next month
                period_start += delta_2
                i += 2
        else:
            i = 0
            for period in self.get_ranges():
                i += 1
                period_start = strptime(
                    str(period.get('date_start', False)), DF)
                period_end = strptime(
                    str(period.get('date_end', False)), DF)
                self._create_single_period(
                    period_start, period_end, i)
        return True

    @api.multi
    def _create_single_period(self, date_start, date_end, number):
        """ Create a single payroll period
        :param date_start: the first day of the actual period
        :param date_end: the first day of the following period
        """
        self.ensure_one()
        period_type = self.env['hr.period']._default_type(self.company_id.id)
        self.write({
            'period_ids': [(0, 0, {
                'date_start': date_start,
                'date_end': date_end,
                'date_payment': self._get_day_of_payment(date_end),
                'company_id': self.company_id.id,
                'name': _('%s Period #%s') % (self.name, number),
                'number': number,
                'state': 'draft',
                'type_id': period_type.id,
                'schedule_pay': self.schedule_pay,
            })],
        })

    @api.multi
    def _get_day_of_payment(self, date_end):
        """
        Get the date of payment for a period to create
        :param date_end: the last day of the current period
        """
        self.ensure_one()

        date_payment = date_end
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
