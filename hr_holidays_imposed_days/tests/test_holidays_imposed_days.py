# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common
from openerp import fields
from dateutil.relativedelta import relativedelta


class TestHolidaysImposedDays(common.TransactionCase):

    def setUp(self):
        super(TestHolidaysImposedDays, self).setUp()
        self.employee_model = self.env['hr.employee']
        self.holiday_status_model = self.env['hr.holidays.status']
        self.holiday_imposed_model = self.env['hr.holidays.imposed']
        self.holiday_model = self.env['hr.holidays']

        # create leave types that we will be manupilating
        self.holiday_type = self.holiday_status_model.create(
            {
                'name': 'Leave',
                'limit': True
            }
        )

        self.today = fields.Datetime.from_string(fields.Datetime.now())

    def test_imposed_number_of_days_computation(self):
        # define an imposed day
        self.imposed = self.holiday_imposed_model.create(
            {'name': 'TEST',
             'date_from': fields.Datetime.to_string(self.today +
                                                    relativedelta(days=2)),
             'date_to': fields.Datetime.to_string(self.today +
                                                  relativedelta(days=4)),
             'status_id': self.holiday_type.id,
             }
            )
        self.imposed.onchange_dates()
        self.assertEqual(self.imposed.number_of_days, 3.)

    def test_imposed_employee_create(self):
        # Create employee
        self.employee = self.employee_model.create({
            'name': 'Employee 1',
        })
        leaves = self.holiday_model.search(
            [('type', '=', 'remove'),
             ('employee_id', '=', self.employee.id)
             ]
        )
        self.assertEqual(len(leaves), 0)

        self.imposed = self.holiday_imposed_model.create(
            {'name': 'TEST',
             'date_from': fields.Datetime.to_string(self.today +
                                                    relativedelta(days=2)),
             'date_to': fields.Datetime.to_string(self.today +
                                                  relativedelta(days=4)),
             'status_id': self.holiday_type.id,
             }
            )
        self.employee2 = self.employee_model.create({
            'name': 'Employee 2',
        })
        leaves = self.holiday_model.search(
            [('type', '=', 'remove'),
             ('employee_id', '=', self.employee2.id)
             ]
        )
        self.assertEqual(len(leaves), 1)
        self.assertEqual(leaves[0].state, 'confirm')

    def test_imposed_employee_create_approved(self):
        # Create employee
        self.employee = self.employee_model.create({
            'name': 'Employee 1',
        })
        leaves = self.holiday_model.search(
            [('type', '=', 'remove'),
             ('employee_id', '=', self.employee.id)
             ]
        )
        self.assertEqual(len(leaves), 0)

        self.imposed = self.holiday_imposed_model.create(
            {'name': 'TEST',
             'date_from': fields.Datetime.to_string(self.today +
                                                    relativedelta(days=2)),
             'date_to': fields.Datetime.to_string(self.today +
                                                  relativedelta(days=4)),
             'status_id': self.holiday_type.id,
             'auto_confirm': True
             }
            )
        self.employee2 = self.employee_model.create({
            'name': 'Employee 2',
        })
        leaves = self.holiday_model.search(
            [('type', '=', 'remove'),
             ('employee_id', '=', self.employee2.id)
             ]
        )
        self.assertEqual(len(leaves), 1)
        self.assertEqual(leaves[0].state, 'validate')

    def test_imposed_employee_create_validate(self):
        # Create employee
        self.employee = self.employee_model.create({
            'name': 'Employee 1',
        })
        self.employee2 = self.employee_model.create({
            'name': 'Employee 2',
        })
        self.imposed = self.holiday_imposed_model.create(
            {'name': 'TEST',
             'date_from': fields.Datetime.to_string(self.today +
                                                    relativedelta(days=2)),
             'date_to': fields.Datetime.to_string(self.today +
                                                  relativedelta(days=4)),
             'status_id': self.holiday_type.id,
             'auto_confirm': True
             }
            )
        self.imposed.validate()
        leaves = self.holiday_model.search(
            [('type', '=', 'remove'),
             ('employee_id', 'in', (self.employee.id, self.employee2.id))]
        )
        self.assertEqual(len(leaves), 2)
        self.assertEqual(leaves[0].state, 'validate')
