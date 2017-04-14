# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import common
from openerp import exceptions
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime


def convert_datetime(str_date):
    date_dt = datetime.strptime(str_date, '%Y-%m-%d')
    return date_dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)


class TestHrHolidaysPreviousType(common.TransactionCase):

    def setUp(self):
        super(TestHrHolidaysPreviousType, self).setUp()
        self.holidays_obj = self.env['hr.holidays']
        self.type01 = self.env.ref('hr_holidays.holiday_status_cl')
        self.type02 = self.type01.copy()
        self.employee01 = self.env.ref('hr.employee_vad')
        self.year = datetime.now().strftime('%Y')
        self.yearp1 = str(int(self.year) + 1)
        self.yearp2 = str(int(self.year) + 2)

    def _prepare_types(self):
        self.type01.use_validity_dates = True
        date_start = convert_datetime('%s-01-01' % self.year)
        date_end = convert_datetime('%s-03-31' % self.yearp1)
        self.type01.date_start = date_start
        self.type01.date_end = date_end

        self.type02.use_validity_dates = True
        date_start = convert_datetime('%s-01-01' % self.yearp1)
        date_end = convert_datetime('%s-03-31' % self.yearp2)
        self.type02.date_start = date_start
        self.type02.date_end = date_end
        self.type02.previous_type_id = self.type01

    def _create_allocation(self):
        allocation_vals = {
            'name': 'Test',
            'type': 'add',
            'employee_id': self.employee01.id,
            'holiday_status_id': self.type01.id,
            'number_of_days_temp': 10,
        }
        alloc = self.holidays_obj.create(allocation_vals)
        alloc.action_validate()
        allocation_vals = {
            'name': 'Test',
            'type': 'add',
            'employee_id': self.employee01.id,
            'holiday_status_id': self.type02.id,
            'number_of_days_temp': 10,
        }
        alloc = self.holidays_obj.create(allocation_vals)
        alloc.action_validate()

    def test_without_previous_type(self):
        self._create_allocation()
        date_start = convert_datetime('%s-01-01' % self.year)
        date_end = convert_datetime('%s-01-05' % self.year)
        leave_vals = {
            'employee_id': self.employee01.id,
            'holiday_status_id': self.type01.id,
            'name': 'test',
            'date_from': date_start,
            'date_to': date_end,
            'number_of_days_temp': 5.0
        }
        self.holidays_obj.create(leave_vals)
        date_start = convert_datetime('%s-03-31' % self.yearp1)
        date_end = convert_datetime('%s-04-01' % self.yearp1)
        leave_vals = {
            'employee_id': self.employee01.id,
            'holiday_status_id': self.type02.id,
            'name': 'test',
            'date_from': date_start,
            'date_to': date_end,
            'number_of_days_temp': 2.0
        }
        self.holidays_obj.create(leave_vals)

    def test_previous_type(self):
        self._prepare_types()
        self._create_allocation()
        date_start = convert_datetime('%s-01-01' % self.year)
        date_end = convert_datetime('%s-01-05' % self.year)
        leave_vals01 = {
            'employee_id': self.employee01.id,
            'holiday_status_id': self.type01.id,
            'name': 'test',
            'date_from': date_start,
            'date_to': date_end,
            'number_of_days_temp': 5.0
        }
        self.holidays_obj.create(leave_vals01)
        date_start = convert_datetime('%s-03-31' % self.yearp1)
        date_end = convert_datetime('%s-04-01' % self.yearp1)
        leave_vals = {
            'employee_id': self.employee01.id,
            'holiday_status_id': self.type02.id,
            'name': 'test',
            'date_from': date_start,
            'date_to': date_end,
            'number_of_days_temp': 2.0
        }
        # I test with a date from before the previous type end date
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            self.holidays_obj.create(leave_vals)
        # I test before the validity date of the previous type
        leave_vals['date_from'] = convert_datetime('%s-03-30' % self.yearp1)
        leave_vals['date_to'] = convert_datetime('%s-03-31' % self.yearp1)
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            self.holidays_obj.create(leave_vals)
        # I test after the validity date of the previous type
        leave_vals['date_from'] = convert_datetime('%s-04-01' % self.yearp1)
        leave_vals['date_to'] = convert_datetime('%s-04-02' % self.yearp1)
        self.holidays_obj.create(leave_vals)
        # I test with no validity dates onthe previous type.
        # An exception should be raised
        self.type01.use_validity_dates = False
        leave_vals['date_from'] = convert_datetime('%s-04-03' % self.yearp1)
        leave_vals['date_to'] = convert_datetime('%s-04-04' % self.yearp1)
        with self.assertRaises(exceptions.ValidationError),\
                self.cr.savepoint():
            self.holidays_obj.create(leave_vals)
        self.type01.use_validity_dates = True
        # I take remaining leaves on the first type
        leave_vals01['date_from'] = convert_datetime('%s-01-01' % self.yearp1)
        leave_vals01['date_to'] = convert_datetime('%s-01-05' % self.yearp1)
        self.holidays_obj.create(leave_vals01)
        # Test with no remaining leaves on the first type
        leave_vals['date_from'] = convert_datetime('%s-03-30' % self.yearp1)
        leave_vals['date_to'] = convert_datetime('%s-03-31' % self.yearp1)
        self.holidays_obj.create(leave_vals)
