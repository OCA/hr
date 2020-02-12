# Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta


class TestHrHolidaysValidityDate(common.TransactionCase):

    at_install = False
    post_install = True

    def setUp(self):
        super(TestHrHolidaysValidityDate, self).setUp()
        self.holidays_obj = self.env['hr.leave']
        self.type01 = self.env['hr.leave.type'].create({
            'name': 'Status',
            'allocation_type': 'no',
            'validity_start': False,
        })
        self.employee01 = self.env['hr.employee'].create({
            'name': 'Employee'
        })

    def test_holidays_without_validity(self):
        today = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        tomorrow = (datetime.now() + timedelta(days=1)).strftime(
            DEFAULT_SERVER_DATETIME_FORMAT
        )
        leave_vals = {
            'employee_id': self.employee01.id,
            'name': 'test',
            'holiday_status_id': self.type01.id,
            'date_from': today,
            'date_to': tomorrow,
            'number_of_days': 1,
        }
        self.holidays_obj.create(leave_vals)

    def test_holidays_validity(self):
        now = datetime.now()
        yesterday = (now - timedelta(days=1)).strftime(
            DEFAULT_SERVER_DATETIME_FORMAT
        )
        today = now.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        tomorrow = (now + timedelta(days=1)).strftime(
            DEFAULT_SERVER_DATETIME_FORMAT
        )
        day_after_tomorrow = (now + timedelta(days=2)).strftime(
            DEFAULT_SERVER_DATETIME_FORMAT
        )

        self.type01.restrict_dates = True
        self.type01.validity_start = yesterday
        self.type01.validity_stop = today

        leave_vals = {
            'employee_id': self.employee01.id,
            'holiday_status_id': self.type01.id,
            'name': 'test',
            'date_from': today,
            'date_to': tomorrow,
            'number_of_days': 2,
        }
        with self.assertRaises(ValidationError):
            self.holidays_obj.create(leave_vals)

        self.type01.restrict_dates = False
        leave_vals = {
            'employee_id': self.employee01.id,
            'holiday_status_id': self.type01.id,
            'name': 'test',
            'date_from': day_after_tomorrow,
            'date_to': day_after_tomorrow,
            'number_of_days': 1,
        }
        holidays = self.holidays_obj.create(leave_vals)
        self.assertIn('Warning', holidays.warning_validity)
