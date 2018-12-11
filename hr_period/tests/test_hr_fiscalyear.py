# Copyright 2015 Savoir-faire Linux. All Rights Reserved.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date

from odoo.tests import common
from odoo import fields
from odoo.exceptions import UserError, ValidationError


class TestHrFiscalyear(common.TransactionCase):
    def setUp(self):
        super(TestHrFiscalyear, self).setUp()
        self.user_model = self.env["res.users"]
        self.company_model = self.env['res.company']
        self.payslip_model = self.env["hr.payslip"]
        self.run_model = self.env['hr.payslip.run']
        self.fy_model = self.env['hr.fiscalyear']
        self.period_model = self.env['hr.period']
        self.data_range_type_model = self.env['date.range.type']

        self.company = self.env.ref('base.main_company')

        self.today = fields.Datetime.now().date()
        self.type_fy = self.create_data_range_type('test_hr_fy', 'fy')
        self.type = self.create_data_range_type('test_hr_period', 'per')
        self.vals = {
            'company_id': self.company.id,
            'date_start': '2015-01-01',
            'date_end': '2015-12-31',
            'schedule_pay': 'monthly',
            'type_id': self.type.id,
            'payment_day': '2',
            'payment_weekday': '0',
            'payment_week': '1',
            'name': 'Test',
        }

    def create_data_range_type(self, name, hr_type, company=False):
        if not company:
            company = self.company
        vals = {'name': name,
                'active': True,
                'company_id': company.id,
                }
        if hr_type == 'per':
            vals.update(hr_period=True)
        else:
            vals.update(hr_fiscal_year=True)
        return self.data_range_type_model.create(vals)

    def create_fiscal_year(self, vals=None):
        if vals is None:
            vals = {}
        if not vals.get('type_id'):
            vals['type_id'] = self.fy_model._default_type().id
        if not vals.get('date_start'):
            vals['date_start'] = self.fy_model._default_date_start()
        if not vals.get('date_end'):
            vals['date_end'] = self.fy_model._default_date_end()
        if vals.get('company_id'):
            vals['company_id'] = vals['company_id']
        if vals.get('schedule_pay'):
            vals['schedule_pay'] = vals['schedule_pay']
        self.vals.update(vals)
        return self.fy_model.create(self.vals)

    def get_periods(self, fiscal_year):
        return fiscal_year.period_ids.sorted(key=lambda p: p.date_start)

    def check_period(self, period, date_start, date_end, date_payment):
        if date_start:
            self.assertEqual(str(period.date_start), date_start)
        if date_end:
            self.assertEqual(str(period.date_end), date_end)
        if date_payment:
            self.assertEqual(str(period.date_payment), date_payment)

    def test_fy_change_scheduled_pay(self):
        fy = self.create_fiscal_year(
            {'date_start': '2015-01-01',
             'date_end': '2015-12-31',
             'type_id': self.type_fy.id,
             })
        fy.schedule_pay = 'weekly'
        fy.onchange_schedule()
        self.assertEqual(fy.name, '2015 - Weekly (52)')

    def test_confirm_periods(self):
        fy = self.create_fiscal_year(
            {'type_id': self.type_fy.id,
             'company_id': self.company.id}
        )
        with self.assertRaises(UserError):
            fy.button_confirm()
        fy.create_periods()
        periods = self.get_periods(fy)
        fy.button_confirm()
        self.assertEqual(periods[0].state, 'open')
        self.assertEqual(periods[1].state, 'draft')

    def test_create_periods_monthly(self):
        fy = self.create_fiscal_year(
            {'date_start': '2015-01-01',
             'date_end': '2015-12-31',
             'type_id': self.type_fy.id,
             })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 12)
        self.check_period(periods[0], '2015-01-01', '2015-01-31', '2015-02-02')
        self.check_period(periods[1], '2015-02-01', '2015-02-28', '2015-03-02')
        self.check_period(periods[2], '2015-03-01', '2015-03-31', '2015-04-02')
        self.check_period(
            periods[11], '2015-12-01', '2015-12-31', '2016-01-02')

    def test_create_periods_monthly_custom_year(self):
        fy = self.create_fiscal_year({
            'date_start': '2015-03-16',
            'date_end': '2016-03-15',
            'type_id': self.type_fy.id,
        })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 12)
        self.check_period(periods[0], '2015-03-16', '2015-04-15', '2015-04-17')
        self.check_period(periods[1], '2015-04-16', '2015-05-15', '2015-05-17')
        self.check_period(periods[2], '2015-05-16', '2015-06-15', '2015-06-17')
        self.check_period(
            periods[11], '2016-02-16', '2016-03-15', '2016-03-17')

    def test_create_periods_semi_monthly(self):
        fy = self.create_fiscal_year(
            {'date_start': '2015-01-01',
             'date_end': '2015-12-31',
             'schedule_pay': 'semi-monthly',
             'type_id': self.type_fy.id,
             })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 24)
        self.check_period(periods[0], '2015-01-01', '2015-01-15', '2015-01-17')
        self.check_period(periods[1], '2015-01-16', '2015-01-31', '2015-02-02')
        self.check_period(periods[2], '2015-02-01', '2015-02-15', '2015-02-17')
        self.check_period(periods[3], '2015-02-16', '2015-02-28', '2015-03-02')
        self.check_period(
            periods[23], '2015-12-16', '2015-12-31', '2016-01-02')

    def test_create_periods_semi_monthly_custom_year(self):
        fy = self.create_fiscal_year({
            'date_start': '2015-03-20',
            'date_end': '2016-03-19',
            'schedule_pay': 'semi-monthly',
            'type_id': self.type_fy.id,
        })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 24)
        self.check_period(periods[0], '2015-03-20', '2015-04-03', '2015-04-05')
        self.check_period(periods[1], '2015-04-04', '2015-04-19', '2015-04-21')
        self.check_period(periods[2], '2015-04-20', '2015-05-04', '2015-05-06')
        self.check_period(
            periods[22], '2016-02-20', '2016-03-05', '2016-03-07')
        self.check_period(
            periods[23], '2016-03-06', '2016-03-19', '2016-03-21')

    def test_create_fy_wrong_dates(self):
        with self.assertRaises(ValidationError):
            self.create_fiscal_year({
                'schedule_pay': 'annually',
                'date_start': '2015-12-31',
                'date_end': '2015-01-01',
                'type_id': self.type_fy.id,
            })

    def test_create_periods_annually(self):
        fy = self.create_fiscal_year(
            {'date_start': '2015-01-01',
             'date_end': '2015-12-31',
             'schedule_pay': 'annually',
             'type_id': self.type_fy.id,
             })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 1)
        self.check_period(periods[0], '2015-01-01', '2015-12-31', '2016-01-02')

    def test_create_periods_semi_annually(self):
        fy = self.create_fiscal_year(
            {'date_start': '2015-01-01',
             'date_end': '2015-12-31',
             'schedule_pay': 'semi-annually',
             'type_id': self.type_fy.id,
             })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 2)
        self.check_period(periods[0], '2015-01-01', '2015-06-30', '2015-07-02')

    def test_create_periods_annually_custom_year(self):
        fy = self.create_fiscal_year({
            'date_start': '2015-03-16',
            'date_end': '2016-03-15',
            'schedule_pay': 'annually',
            'type_id': self.type_fy.id,
        })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 1)
        self.check_period(periods[0], '2015-03-16', '2016-03-15', '2016-03-17')

    def test_create_periods_weekly(self):
        fy = self.create_fiscal_year(
            {'date_start': '2015-01-01',
             'date_end': '2015-12-31',
             'schedule_pay': 'weekly',
             'type_id': self.type_fy.id,
             })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 52)
        self.check_period(periods[0], '2015-01-01', '2015-01-07', '2015-01-11')
        self.check_period(periods[1], '2015-01-08', '2015-01-14', '2015-01-18')
        self.check_period(periods[2], '2015-01-15', '2015-01-21', '2015-01-25')
        self.check_period(
            periods[51], '2015-12-24', '2015-12-30', '2016-01-03')

    def test_create_periods_weekly_payment_same_week(self):

        fy = self.create_fiscal_year({
            'schedule_pay': 'weekly',
            'payment_week': '0',
            'date_start': '2015-01-01',
            'date_end': '2015-12-31',
            'type_id': self.type_fy.id
        })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 52)
        self.assertEqual(periods[0].date_payment, date(2015, 1, 4))
        self.assertEqual(periods[1].date_payment, date(2015, 1, 11))
        self.assertEqual(periods[2].date_payment, date(2015, 1, 18))
        self.assertEqual(periods[51].date_payment, date(2015, 12, 27))

    def test_create_periods_weekly_payment_2_weeks(self):
        fy = self.create_fiscal_year({
            'schedule_pay': 'weekly',
            'payment_week': '2',
            'date_start': '2015-01-01',
            'date_end': '2015-12-31',
            'type_id': self.type_fy.id
        })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 52)
        self.assertEqual(periods[0].date_payment, date(2015, 1, 18))
        self.assertEqual(periods[1].date_payment, date(2015, 1, 25))
        self.assertEqual(periods[2].date_payment, date(2015, 2, 1))
        self.assertEqual(periods[51].date_payment, date(2016, 1, 10))

    def test_create_periods_monthly_payment_fifth_day(self):
        fy = self.create_fiscal_year({
            'payment_day': '5',
            'date_start': '2015-01-01',
            'date_end': '2015-12-31',
            'type_id': self.type_fy.id
        })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 12)
        self.assertEqual(periods[0].date_payment, date(2015, 2, 5))
        self.assertEqual(periods[1].date_payment, date(2015, 3, 5))
        self.assertEqual(periods[2].date_payment, date(2015, 4, 5))
        self.assertEqual(periods[11].date_payment, date(2016, 1, 5))

    def test_create_periods_monthly_payment_last_day(self):
        fy = self.create_fiscal_year({
            'payment_day': '0',
            'date_start': '2015-01-01',
            'date_end': '2015-12-31',
            'type_id': self.type_fy.id
        })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 12)
        self.assertEqual(periods[0].date_payment, date(2015, 1, 31))
        self.assertEqual(periods[1].date_payment, date(2015, 2, 28))
        self.assertEqual(periods[2].date_payment, date(2015, 3, 31))
        self.assertEqual(periods[11].date_payment, date(2015, 12, 31))

    def test_create_periods_semi_monthly_payment_fifth_day(self):
        fy = self.create_fiscal_year({
            'payment_day': '5',
            'date_start': '2015-01-01',
            'date_end': '2015-12-31',
            'type_id': self.type_fy.id
        })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 12)
        self.assertEqual(periods[0].date_payment, date(2015, 2, 5))
        self.assertEqual(periods[1].date_payment, date(2015, 3, 5))
        self.assertEqual(periods[2].date_payment, date(2015, 4, 5))
        self.assertEqual(periods[11].date_payment, date(2016, 1, 5))

    def test_create_periods_semi_monthly_payment_last_day(self):
        fy = self.create_fiscal_year({
            'schedule_pay': 'semi-monthly',
            'payment_day': '0',
            'date_start': '2015-03-20',
            'date_end': '2016-03-19',
            'type_id': self.type_fy.id
        })
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 24)
        self.assertEqual(periods[0].date_payment, date(2015, 4, 3))
        self.assertEqual(periods[1].date_payment, date(2015, 4, 19))
        self.assertEqual(periods[2].date_payment, date(2015, 5, 4))
        self.assertEqual(periods[22].date_payment, date(2016, 3, 5))
        self.assertEqual(periods[23].date_payment, date(2016, 3, 19))
