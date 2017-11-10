# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of hr_holidays_validity_date,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     hr_holidays_validity_date is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     hr_holidays_validity_date is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with hr_holidays_validity_date.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo.tests import common
from odoo import exceptions
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta


class TestHrHolidaysValidityDate(common.TransactionCase):

    def setUp(self):
        super(TestHrHolidaysValidityDate, self).setUp()
        self.holidays_obj = self.env['hr.holidays']
        self.type01 = self.env.ref('hr_holidays.holiday_status_cl')
        self.employee01 = self.env.ref('hr.employee_root')

    def test_holidays_without_validity(self):
        today = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        tommorow = (datetime.now() + timedelta(days=1))\
            .strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        allocation_vals = {
            'name': 'Test',
            'type': 'add',
            'employee_id': self.employee01.id,
            'holiday_status_id': self.type01.id,
            'number_of_days_temp': 10,
        }
        self.holidays_obj.create(allocation_vals)
        leave_vals = {
            'employee_id': self.employee01.id,
            'name': 'test',
            'holiday_status_id': self.type01.id,
            'date_from': today,
            'date_to': tommorow,
            'number_of_days_temp': 2,
        }
        self.holidays_obj.create(leave_vals)

    def test_holidays_validity(self):
        yesterday = (datetime.now() - timedelta(days=1))\
            .strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        today = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        tommorow = (datetime.now() + timedelta(days=1))\
            .strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.type01.use_validity_dates = True
        self.type01.date_start = yesterday
        self.type01.date_end = today
        allocation_vals = {
            'name': 'Test',
            'type': 'add',
            'employee_id': self.employee01.id,
            'holiday_status_id': self.type01.id,
            'number_of_days_temp': 10,
        }
        self.holidays_obj.create(allocation_vals)
        leave_vals = {
            'employee_id': self.employee01.id,
            'holiday_status_id': self.type01.id,
            'name': 'test',
            'date_from': today,
            'date_to': tommorow,
            'number_of_days_temp': 2,
        }
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            self.holidays_obj.create(leave_vals)
