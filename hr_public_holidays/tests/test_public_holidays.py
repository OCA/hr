# -*- coding: utf-8 -*-
# ©  2015 Salton Massally <smassally@idtlabs.sl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.exceptions import Warning as UserError
from odoo.tests import common
from odoo.tools import mute_logger


class TestPublicHolidays(common.TransactionCase):

    def setUp(self):
        super(TestPublicHolidays, self).setUp()
        self.holiday_model = self.env["hr.holidays.public"]
        self.holiday_model_line = self.env["hr.holidays.public.line"]
        self.employee_model = self.env['hr.employee']
        self.wizard_next_year = self.env['public.holidays.next.year.wizard']

        # Remove possibly existing public holidays that would interfer.
        self.holiday_model_line.search([]).unlink()
        self.holiday_model.search([]).unlink()

        # Create holidays
        holiday2 = self.holiday_model.create({
            'year': 1994,
            'country_id': self.env.ref('base.sl').id
        })
        self.holiday_model_line.create({
            'name': 'holiday 5',
            'date': '1994-10-14',
            'year_id': holiday2.id
        })
        holiday3 = self.holiday_model.create({
            'year': 1994,
            'country_id': self.env.ref('base.sk').id
        })
        self.holiday_model_line.create({
            'name': 'holiday 6',
            'date': '1994-11-14',
            'year_id': holiday3.id
        })

        holiday1 = self.holiday_model.create({
            'year': 1995,
        })
        for dt in ['1995-10-14', '1995-12-31', '1995-01-01']:
            self.holiday_model_line.create({
                'name': 'holiday x',
                'date': dt,
                'year_id': holiday1.id
            })

        self.employee = self.employee_model.create(
            {
                'name': 'Employee 1',
                'address_id': self.env['res.partner'].create(
                    {
                        'name': 'Employee 1',
                        'country_id': self.env.ref('base.sl').id
                    }
                ).id
            }
        )

    def test_duplicate_year_country_fail(self):
        # ensures that duplicate year cannot be created for the same country
        with mute_logger('odoo.models'):
            with self.assertRaises(ValidationError):
                self.holiday_model.create({
                    'year': 1995,
                })
            with self.assertRaises(ValidationError):
                self.holiday_model.create({
                    'year': 1994,
                    'country_id': self.env.ref('base.sl').id
                })

    def test_duplicate_date_state_fail(self):
        # ensures that duplicate date cannot be created for the same country
        # state or with state null
        holiday4 = self.holiday_model.create({
            'year': 1994,
            'country_id': self.env.ref('base.us').id
        })
        with mute_logger('odoo.models'):
            with self.assertRaises(ValidationError):
                self.holiday_model_line.create({
                    'name': 'holiday x',
                    'date': '1994-11-14',
                    'year_id': holiday4.id
                })
                self.holiday_model_line.create({
                    'name': 'holiday x',
                    'date': '1994-11-14',
                    'year_id': holiday4.id
                })
            with self.assertRaises(ValidationError):
                self.holiday_model_line.create({
                    'name': 'holiday x',
                    'date': '1994-11-14',
                    'year_id': holiday4.id,
                    'state_ids': [(6, 0,
                                   [self.env.ref('base.state_us_35').id])]
                })
                self.holiday_model_line.create({
                    'name': 'holiday x',
                    'date': '1994-11-14',
                    'year_id': holiday4.id,
                    'state_ids': [(6, 0,
                                   [self.env.ref('base.state_us_35').id])]
                })

    def test_isnot_holiday(self):
        # ensures that if given a date that is not an holiday it returns none
        self.assertFalse(self.holiday_model.is_public_holiday('1995-12-10'))

    def test_is_holiday(self):
        # ensures that correct holidays are identified
        self.assertTrue(self.holiday_model.is_public_holiday('1995-10-14'))

    def test_isnot_holiday_in_country(self):
        # ensures that correct holidays are identified for a country
        self.assertFalse(self.holiday_model.is_public_holiday(
            '1994-11-14', employee_id=self.employee.id))

    def test_is_holiday_in_country(self):
        # ensures that correct holidays are identified for a country
        self.assertTrue(self.holiday_model.is_public_holiday(
            '1994-10-14', employee_id=self.employee.id))

    def test_list_holidays_in_list_country_specific(self):
        # ensures that correct holidays are identified for a country
        lines = self.holiday_model.get_holidays_list(
            1994, employee_id=self.employee.id)
        res = lines.filtered(lambda r: r.date == '1994-10-14')
        self.assertEqual(len(res), 1)
        self.assertEqual(len(lines), 1)

    def test_list_holidays_in_list(self):
        # ensures that correct holidays are identified for a country
        lines = self.holiday_model.get_holidays_list(1995)
        res = lines.filtered(lambda r: r.date == '1995-10-14')
        self.assertEqual(len(res), 1)
        self.assertEqual(len(lines), 3)

    def test_create_next_year_public_holidays(self):
        self.wizard_next_year.new().create_public_holidays()
        lines = self.holiday_model.get_holidays_list(1996)
        res = lines.filtered(lambda r: r.date == '1996-10-14')
        self.assertEqual(len(res), 1)
        self.assertEqual(len(lines), 3)

    def test_create_year_2000_public_holidays(self):
        ph_start_ids = self.holiday_model.search([('year', '=', 1994)])
        val = {
            'template_ids': ph_start_ids,
            'year': 2000
        }
        wz_create_ph = self.wizard_next_year.new(values=val)
        wz_create_ph.onchange_year_template_ids()

        wz_create_ph.create_public_holidays()

        lines = self.holiday_model.get_holidays_list(2000)
        self.assertEqual(len(lines), 2)

        res = lines.filtered(
            lambda r: r.year_id.country_id.id == self.env.ref('base.sl').id)
        self.assertEqual(len(res), 1)

    def test_create_year_2000_public_holidays_with_date_change(self):
        ph_start_ids = self.holiday_model.search([('year', '=', 1994)])

        # Set 1994-10-14 as a variable holiday
        october_fourteenth = ph_start_ids.mapped('line_ids').filtered(
            lambda d: d.date == '1994-10-14'
        )
        october_fourteenth.variable = True
        val = {
            'template_ids': ph_start_ids,
            'year': 2000
        }
        wz_create_ph = self.wizard_next_year.new(values=val)
        wz_create_ph.onchange_year_template_ids()
        self.assertEqual(
            len(wz_create_ph.public_holidays_next_year_day_ids), 2)
        october_fourteenth_line = \
            wz_create_ph.public_holidays_next_year_day_ids.filtered(
                lambda d: d.variable)
        self.assertEqual(october_fourteenth_line.last_date, '1994-10-14')
        october_fourteenth_line.next_date = '2000-10-15'

        wz_create_ph.create_public_holidays()

        lines = self.holiday_model.get_holidays_list(2000)
        self.assertEqual(len(lines), 2)

        res = lines.filtered(
            lambda r: r.year_id.country_id.id == self.env.ref('base.sl').id)
        self.assertEqual(len(res), 1)
        # Check the new holiday is created on 15th and not 14th
        self.assertEqual(
            len(lines.filtered(lambda r: r.date == '2000-10-14')), 0)
        self.assertEqual(
            len(lines.filtered(lambda r: r.date == '2000-10-15')), 1)

    def test_february_29th(self):
        # Ensures that users get a UserError (not a nasty Exception) when
        # trying to create public holidays from year including 29th of
        # February
        holiday_tw_2016 = self.holiday_model.create({
            'year': 2016,
            'country_id': self.env.ref('base.tw').id
        })

        self.holiday_model_line.create({
            'name': 'Peace Memorial Holiday',
            'date': '2016-02-29',
            'year_id': holiday_tw_2016.id,
        })

        val = {
            'template_ids': holiday_tw_2016
        }
        wz_create_ph = self.wizard_next_year.new(values=val)

        with self.assertRaises(UserError):
            wz_create_ph.create_public_holidays()
