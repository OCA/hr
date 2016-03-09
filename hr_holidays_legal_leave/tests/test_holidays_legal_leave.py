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
from openerp.exceptions import Warning as UserWarning


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
        for sig in ('confirm', 'validate', 'second_validate'):
            self.holiday.signal_workflow(sig)

    def test_try_reduce_allocation(self):
        # let's sattempt to reduce allocation here... it should not let us
        with self.assertRaises(UserWarning):
            self.employee.write({'remaining_leaves': 5})

    def test_getting_remaining(self):
        # let's attempt getting remaining leave
        self.assertEqual(self.employee.remaining_leaves, 10)

    def test_setting_remaining(self):
        # let's attempt setting remaining leave
        self.employee.write({'remaining_leaves': 20})
        self.assertEqual(self.employee.remaining_leaves, 20)
