# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2015 Salton Massally (<smassally@idtlabs.sl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from openerp.tests import common
from openerp.exceptions import ValidationError


class TestPublicHolidays(common.TransactionCase):

    def setUp(self):
        super(TestPublicHolidays, self).setUp()
        self.holiday_model = self.env["hr.holidays.public"]
        self.holiday_model_line = self.env["hr.holidays.public.line"]
        self.employee_model = self.env['hr.employee']

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
        with self.assertRaises(ValidationError):
            self.holiday = self.holiday_model.create({
                'year': 1995,
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
        lines =  self.holiday_model.get_holidays_list(
            1994, employee_id=self.employee.id) 
        self.assertIn('1994-10-14', lines)
        self.assertEqual(len(lines), 1)

    def test_list_holidays_in_list(self):
        # ensures that correct holidays are identified for a country
        lines = self.holiday_model.get_holidays_list(1995)
        self.assertIn('1995-10-14', lines)
        self.assertEqual(len(lines), 3)
