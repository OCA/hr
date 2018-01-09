# Author: Damien Crier
# Copyright 2016-2018 Camptocamp SA
# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo.tests import common
from odoo.exceptions import ValidationError
from odoo import fields


class TestHolidaysImposedDays(common.TransactionCase):

    def setUp(self):
        super(TestHolidaysImposedDays, self).setUp()

        # create leave types that we will be manipulating
        self.holiday_type = self.env['hr.holidays.status'].create({
            'name': 'Leave',
            'limit': True
        })

        # Create employees
        self.employee = self.env['hr.employee'].create({
            'name': 'Employee 1',
        })
        self.employee2 = self.env['hr.employee'].create({
            'name': 'Employee 2',
        })

        dt_from = fields.Datetime.from_string(
            fields.Datetime.now()
        ) + relativedelta(days=32)
        dt_to = dt_from + relativedelta(days=2)
        self.date_from = fields.Datetime.to_string(dt_from)
        self.date_to = fields.Datetime.to_string(dt_to)

    def test_01_number_of_days_computation(self):
        # define an imposed day
        self.imposed = self.env['hr.holidays.imposed'].create({
            'name': 'TEST',
            'date_from': self.date_from,
            'date_to': self.date_to,
            'status_id': self.holiday_type.id,
        })
        self.imposed.onchange_dates()
        self.assertEqual(self.imposed.number_of_days, 3.)

    def test_02_on_specific_employee(self):
        # define an imposed day
        self.imposed = self.env['hr.holidays.imposed'].create({
            'name': 'TEST',
            'date_from': self.date_from,
            'date_to': self.date_to,
            'status_id': self.holiday_type.id,
            'employee_ids': [(4, self.employee.id)],
        })
        self.imposed.validate()
        leaves = self.env['hr.holidays'].search([
            ('type', '=', 'remove'),
            ('employee_id', '=', self.employee.id)
        ])
        self.assertEqual(len(leaves), 1)
        self.assertEqual(leaves[0].state, 'confirm')

    def test_03_employee_create(self):
        leaves = self.env['hr.holidays'].search([
            ('type', '=', 'remove'),
            ('employee_id', '=', self.employee.id)
        ])
        self.assertEqual(len(leaves), 0)
        leaves = self.env['hr.holidays'].search([
            ('type', '=', 'remove'),
            ('employee_id', '=', self.employee2.id)
        ])
        self.assertEqual(len(leaves), 0)

        self.imposed = self.env['hr.holidays.imposed'].create({
            'name': 'TEST',
            'date_from': self.date_from,
            'date_to': self.date_to,
            'status_id': self.holiday_type.id,
        })
        leaves = self.env['hr.holidays'].search([
            ('type', '=', 'remove'),
            ('employee_id', '=', self.employee.id)
        ])
        self.assertEqual(len(leaves), 0)
        leaves = self.env['hr.holidays'].search([
            ('type', '=', 'remove'),
            ('employee_id', '=', self.employee2.id)
        ])
        self.assertEqual(len(leaves), 0)

    def test_04_employee_create_approved(self):
        leaves = self.env['hr.holidays'].search([
            ('type', '=', 'remove'),
            ('employee_id', '=', self.employee.id)
        ])
        self.assertEqual(len(leaves), 0)
        leaves = self.env['hr.holidays'].search([
            ('type', '=', 'remove'),
            ('employee_id', '=', self.employee2.id)
        ])
        self.assertEqual(len(leaves), 0)

        self.imposed = self.env['hr.holidays.imposed'].create({
            'name': 'TEST',
            'date_from': self.date_from,
            'date_to': self.date_to,
            'status_id': self.holiday_type.id,
            'auto_confirm': True
        })
        leaves = self.env['hr.holidays'].search([
            ('type', '=', 'remove'),
            ('employee_id', '=', self.employee.id)
        ])
        self.assertEqual(len(leaves), 0)
        leaves = self.env['hr.holidays'].search([
            ('type', '=', 'remove'),
            ('employee_id', '=', self.employee2.id)
        ])
        self.assertEqual(len(leaves), 0)

    def test_05_employee_create_validate(self):
        self.imposed = self.env['hr.holidays.imposed'].create({
            'name': 'TEST',
            'date_from': self.date_from,
            'date_to': self.date_to,
            'status_id': self.holiday_type.id,
            'auto_confirm': True
        })
        self.imposed.validate()
        leaves = self.env['hr.holidays'].search([
            ('type', '=', 'remove'),
            ('employee_id', 'in', (self.employee.id, self.employee2.id))
        ])
        self.assertEqual(len(leaves), 2)
        self.assertEqual(leaves[0].state, 'validate')

    def test_06_same_dates(self):
        # define an imposed day
        self.imposed = self.env['hr.holidays.imposed'].create({
            'name': 'TEST',
            'date_from': self.date_from,
            'date_to': self.date_from,
            'status_id': self.holiday_type.id,
        })
        self.imposed.onchange_dates()
        self.assertEqual(self.imposed.number_of_days, 1.)
        self.imposed.date_from = self.date_from
        self.imposed.date_to = self.date_to
        self.imposed.onchange_dates()
        self.assertEqual(self.imposed.number_of_days, 3.)
        self.imposed.date_from = self.imposed.date_to
        self.imposed.onchange_dates()
        self.assertEqual(self.imposed.number_of_days, 1.)

    def test_07_check_dates_constrains(self):
        with self.assertRaises(ValidationError):
            self.env['hr.holidays.imposed'].create({
                'name': 'TEST',
                'date_from': self.date_to,
                'date_to': self.date_from,
                'status_id': self.holiday_type.id,
                'auto_confirm': True
            })
