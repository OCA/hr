# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by
#    the Free Software Foundation, either version 3 of the License, or
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

from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _

from datetime import datetime
strftime = datetime.strptime

from dateutil.relativedelta import relativedelta

from itertools import chain

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


def get_schedules(self, cr, uid, context=None):
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


def get_payment_days(self, cr, uid, context=None):
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


class HrFiscalYear(orm.Model):
    _name = 'hr.fiscalyear'
    _description = 'HR Fiscal Year'
    _columns = {
        'name': fields.char(
            'Fiscal Year', required=True,
            readonly=True, states={'draft': [('readonly', False)]},
        ),
        'company_id': fields.many2one(
            'res.company', 'Company', required=True,
            readonly=True, states={'draft': [('readonly', False)]},
        ),
        'date_start': fields.date(
            'Start Date', required=True,
            readonly=True, states={'draft': [('readonly', False)]},
            help="The first day of the first period of the fiscal year."
        ),
        'date_stop': fields.date(
            'End Date', required=True,
            readonly=True, states={'draft': [('readonly', False)]},
            help="The last day of the last period of the fiscal year."
        ),
        'period_ids': fields.one2many(
            'hr.period', 'fiscalyear_id', 'Periods',
            readonly=True, states={'draft': [('readonly', False)]},
        ),
        'state': fields.selection([
            ('draft', 'Draft'), ('open', 'Open'), ('done', 'Closed'),
        ], 'Status', readonly=True),
        'schedule_pay': fields.selection(
            get_schedules, 'Scheduled Pay', required=True,
            readonly=True, states={'draft': [('readonly', False)]},
        ),
        'payment_weekday': fields.selection(
            [
                ('0', 'Sunday'),
                ('1', 'Monday'),
                ('2', 'Tuesday'),
                ('3', 'Wednesday'),
                ('4', 'Thursday'),
                ('5', 'Friday'),
                ('6', 'Saturday'),
            ], 'Day of Payment',
            readonly=True, states={'draft': [('readonly', False)]},
        ),
        'payment_week': fields.selection(
            [
                ('0', 'Same Week'),
                ('1', 'Following Week'),
                ('2', 'Second Following Week'),
            ], 'Week of Payment',
            readonly=True, states={'draft': [('readonly', False)]},
        ),
        'payment_day': fields.selection(
            get_payment_days, 'Day of Payment',
            readonly=True, states={'draft': [('readonly', False)]},
        ),
    }

    def _default_date_start(self, cr, uid, context):
        today = datetime.now()
        return datetime(today.year, 1, 1).strftime(
            DEFAULT_SERVER_DATE_FORMAT)

    def _default_date_stop(self, cr, uid, context):
        today = datetime.now()
        return datetime(today.year, 12, 31).strftime(
            DEFAULT_SERVER_DATE_FORMAT)

    _defaults = {
        'state': 'draft',
        'company_id': lambda self, cr, uid, c:
        self.pool['res.users'].browse(cr, uid, uid, c).company_id.id,
        'date_start': _default_date_start,
        'date_stop': _default_date_stop,
        'schedule_pay': 'monthly',
    }

    def onchange_schedule(
        self, cr, uid, ids, schedule_pay, date_start, context=None
    ):
        res = {'value': {}}

        year = datetime.strptime(
            date_start, DEFAULT_SERVER_DATE_FORMAT).year

        schedule_name = next((
            s[1] for s in get_schedules(self, cr, uid, context=context)
            if s[0] == schedule_pay
        ), False)

        res['value']['name'] = '%(year)s - %(schedule)s' % {
            'year': year,
            'schedule': schedule_name,
        }

        return res

    def create_periods(self, cr, uid, ids, context=None):
        """ Create every periods a payroll fiscal year
        """
        if isinstance(ids, (int, long)):
            ids = [ids]

        for fy in self.browse(cr, uid, ids, context=context):

            for period in fy.period_ids:
                period.unlink()

            fy.refresh()

            period_start = datetime.strptime(
                fy.date_start, DEFAULT_SERVER_DATE_FORMAT)

            next_year_start = datetime.strptime(
                fy.date_stop,
                DEFAULT_SERVER_DATE_FORMAT) + relativedelta(days=1)

            # Case for semi-monthly schedules
            if fy.schedule_pay == 'semi-monthly':
                delta_1 = relativedelta(days=15)
                delta_2 = relativedelta(months=1)

                i = 1
                while not period_start + delta_2 > next_year_start:
                    # create periods for one month
                    half_month = period_start + delta_1
                    fy._create_single_period(period_start, half_month, i)
                    fy._create_single_period(
                        half_month, period_start + delta_2, i + 1)

                    # setup for next month
                    period_start += delta_2
                    i += 2

            # All other cases
            else:
                delta, nb_periods = INTERVALS[fy.schedule_pay]

                i = 1
                while not period_start + delta > next_year_start:
                    fy._create_single_period(
                        period_start, period_start + delta, i)
                    period_start += delta
                    i += 1

    def _create_single_period(
        self, cr, uid, ids, date_start, date_stop, number, context=None
    ):
        """ Create a single payroll period
        :param date_start: the first day of the actual period
        :param date_stop: the first day of the following period
        """
        if isinstance(ids, (int, long)):
            ids = [ids]

        assert(len(ids) == 1)

        fy = self.browse(cr, uid, ids[0], context=context)

        date_stop -= relativedelta(days=1)

        fy.write({
            'period_ids': [(0, 0, {
                'date_start': date_start,
                'date_stop': date_stop,
                'date_payment': fy._get_day_of_payment(date_stop),
                'company_id': fy.company_id.id,
                'name': _('%s Period #%s') % (fy.name, number),
                'number': number,
                'state': 'draft',
                'schedule_pay': fy.schedule_pay,
            })],
        })

    def _get_day_of_payment(self, cr, uid, ids, date_stop, context=None):
        """ Get the date of payment for a period to create
        :param date_stop: the last day of the current period
        """
        if isinstance(ids, (int, long)):
            ids = [ids]

        assert(len(ids) == 1)

        fy = self.browse(cr, uid, ids[0], context=context)

        date_payment = date_stop

        if fy.schedule_pay in ['weekly', 'bi-weekly']:
            date_payment += relativedelta(weeks=int(fy.payment_week))

            while date_payment.strftime('%w') != fy.payment_weekday:
                date_payment -= relativedelta(days=1)

        else:
            date_payment += relativedelta(days=int(fy.payment_day))

        return date_payment

    def button_confirm(self, cr, uid, ids, context=None):
        fiscal_years = self.browse(cr, uid, ids, context=context)

        for fy in fiscal_years:
            if not fy.period_ids:
                raise orm.except_orm(
                    _('Warning'),
                    _('You must create periods before confirming the '
                        'the fiscal year.'))

        self.write(cr, uid, ids, {'state': 'open'})

        for fy in fiscal_years:
            first_period = sorted(fy.period_ids, key=lambda p: p.number)[0]
            first_period.button_open()

    def button_set_to_draft(self, cr, uid, ids, context=None):
        # Set all periods to draft
        period_ids = [
            p.id for p in chain(*[
                fy.period_ids for fy in self.browse(
                    cr, uid, ids, context=context)
            ])
        ]

        self.pool['hr.period'].button_set_to_draft(
            cr, uid, period_ids, context=context)

        # Set the fiscal year to draft
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def search_period(self, cr, uid, ids, number, context=None):
        if not ids:
            return False

        if isinstance(ids, (int, long)):
            ids = [ids]

        fy = self.browse(cr, uid, ids[0], context=context)

        return next((p for p in fy.period_ids if p.number == number), False)
