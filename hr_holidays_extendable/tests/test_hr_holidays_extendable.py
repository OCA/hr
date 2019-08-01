# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestHrHolidaysExtendable(TransactionCase):

    def setUp(self):
        super(TestHrHolidaysExtendable, self).setUp()
        self.employee = self.env['hr.employee'].create({
            'name': 'Employee 1',
        })
        self.holiday_type = self.env['hr.holidays.status'].create({
            'name': 'Leave Type Test',
            'extendable': True,
        })
        self.allocation = self.env['hr.holidays'].create({
            'name': 'Test',
            'type': 'add',
            'employee_id': self.employee.id,
            'holiday_status_id': self.holiday_type.id,
            'number_of_days_temp': 10,
        })
        self.allocation.action_validate()

    def test_hr_holidays_extendable(self):
        holiday = self.env['hr.holidays'].create({
            'name': 'Test',
            'type': 'remove',
            'employee_id': self.employee.id,
            'holiday_status_id': self.holiday_type.id,
            'date_from': '2019-05-21 12:00:00',
            'date_to': '2019-05-22 11:59:59',
            'number_of_days_temp': 2,
        })
        holiday.action_validate()
        remaining_days = self.holiday_type.get_days(
            self.employee.id)[self.holiday_type.id]['remaining_leaves']
        self.assertEqual(remaining_days, 8)

        wizard = self.env['wizard.extend.holidays'].with_context(
            {'active_id': holiday.id}
        ).create({})
        self.assertEqual(wizard.holidays_id.id, holiday.id)
        wizard.write({'date_to': '2019-05-23 11:59:59'})
        wizard.extend_holidays()

        self.assertEqual(holiday.date_to, '2019-05-23 11:59:59')
        self.assertEqual(holiday.number_of_days, -3)
        remaining_days = self.holiday_type.get_days(
            self.employee.id)[self.holiday_type.id]['remaining_leaves']
        self.assertEqual(remaining_days, 7)

        # check constraint
        wizard = self.env['wizard.extend.holidays'].with_context(
            {'active_id': holiday.id}
        ).create({})
        with self.assertRaises(ValidationError):
            wizard.write({'date_to': '2019-05-19'})
