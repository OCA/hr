# -*- coding: utf-8 -*-
# ©  2015 iDT LABS (http://www.@idtlabs.sl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common
from openerp.exceptions import Warning as UserError


class TestHolidaysLegalLeave(common.TransactionCase):

    def setUp(self):
        super(TestHolidaysLegalLeave, self).setUp()
        self.employee_model = self.env['hr.employee']
        self.holiday_status_model = self.env['hr.holidays.status']
        self.holiday_model = self.env['hr.holidays']

        self.company = self.env.ref('base.main_company')

        # Create an employees
        self.employee = self.employee_model.create({
            'name': 'Employee 1',
        })

        # create leave type
        self.holiday_status = self.holiday_status_model.create(
            {
                'name': 'Leave',
                'limit': True,
            }
        )
        self.company.legal_holidays_status_id = self.holiday_status.id
        self.holiday = self.holiday_model.create({
            'name': 'Hol10',
            'employee_id': self.employee.id,
            'type': 'add',
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_status.id,
            'number_of_days_temp': 10
        })
        self.holiday.action_approve()

    def test_try_reduce_allocation(self):
        # let's sattempt to reduce allocation here... it should not let us
        with self.assertRaises(UserError):
            self.employee.write({'remaining_leaves': 5})

    def test_getting_remaining(self):
        # let's attempt getting remaining leave
        self.assertEqual(self.employee.remaining_leaves, 10)

    def test_setting_remaining(self):
        # let's attempt setting remaining leave
        self.employee.write({'remaining_leaves': 20})
        self.assertEqual(self.employee.remaining_leaves, 20)

    def test_create_employee(self):
        """Check that we are able to create new employee
        and that _inverse_remaining_days doesn't raise error"""
        self.employee_model.create({
            'name': 'Employee 1',
            'remaining_leaves': 0,
        })
