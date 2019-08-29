# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import common

from dateutil.relativedelta import relativedelta
from datetime import date
from mock import patch


class TestHrEmployeeService(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.today = fields.Date.today()
        self.now = fields.Datetime.now()
        self.Employee = self.env['hr.employee']
        self.SudoEmployee = self.Employee.sudo()

    def test_1(self):
        employee = self.SudoEmployee.create({
            'name': 'Employee #1',
            'service_hire_date': (
                self.today - relativedelta(years=3)
            ),
            'service_start_date': (
                self.today - relativedelta(years=3)
            ),
            'service_termination_date': (
                self.today - relativedelta(years=1)
            ),
        })

        self.assertEqual(employee.service_duration_years, 2)
        self.assertEqual(employee.service_duration_months, 0)
        self.assertEqual(employee.service_duration_days, 0)

    def test_2(self):
        employee = self.SudoEmployee.create({
            'name': 'Employee #2',
            'service_hire_date': (
                self.today - relativedelta(years=3)
            ),
            'service_start_date': (
                self.today - relativedelta(years=3)
            ),
        })

        self.assertEqual(employee.service_duration_years, 3)
        self.assertEqual(employee.service_duration_months, 0)
        self.assertEqual(employee.service_duration_days, 0)

    def test_3(self):
        mocked_today = date(2019, 8, 27)
        employee = self.SudoEmployee.create({
            'name': 'Employee #3',
            'service_hire_date': (
                mocked_today - relativedelta(months=6)
            ),
            'service_start_date': (
                mocked_today - relativedelta(months=6)
            ),
        })

        with patch('odoo.fields.Date.today') as today:
            today.return_value = mocked_today
            self.assertEqual(employee.service_duration_years, 0)
            self.assertEqual(employee.service_duration_months, 6)
            self.assertEqual(employee.service_duration_days, 0)

    def test_4(self):
        employee = self.SudoEmployee.create({
            'name': 'Employee #4',
            'service_hire_date': (
                self.today - relativedelta(months=6)
            ),
        })

        self.assertEqual(employee.service_duration_years, 0)
        self.assertEqual(employee.service_duration_months, 0)
        self.assertEqual(employee.service_duration_days, 0)

    def test_5(self):
        employee = self.SudoEmployee.create({
            'name': 'Employee #5',
            'service_hire_date': (
                self.today - relativedelta(days=1)
            ),
            'service_start_date': (
                self.today - relativedelta(days=1)
            ),
        })

        self.assertEqual(employee.service_duration, 1)
        self.assertEqual(employee.service_duration_days, 1)

    def test_6(self):
        employee = self.SudoEmployee.create({
            'name': 'Employee #6',
            'service_hire_date': self.today,
            'service_start_date': self.today,
        })

        employee.service_hire_date = None
        employee.service_start_date = None

        self.assertEqual(employee.service_duration_years, 0)
        self.assertEqual(employee.service_duration_months, 0)
        self.assertEqual(employee.service_duration_days, 0)

    def test_7(self):
        employee = self.SudoEmployee.create({
            'name': 'Employee #7',
            'service_hire_date': (
                self.today - relativedelta(days=1)
            ),
        })

        employee._onchange_service_hire_date()

        self.assertEqual(employee.service_duration_years, 0)
        self.assertEqual(employee.service_duration_months, 0)
        self.assertEqual(employee.service_duration_days, 1)
