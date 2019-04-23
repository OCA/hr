import odoo.tests.common as common


class TestPersonalDays(common.TransactionCase):

    def setUp(self):
        super(TestPersonalDays, self).setUp()

        HolidaysStatus = self.env['hr.holidays.status']
        Employee = self.env['hr.employee']

        self.employee1 = Employee.create({
            'name': 'Employee 1',
        })
        self.status = HolidaysStatus.create({
            'name': 'Aprils Holidays',
            'period_from': '2019-04-01',
            'period_to': '2019-04-30',
        })

    def test_personal_days_warning(self):
        holiday1 = self.env['hr.holidays'].new({
            'date_from': '2019-04-20 10:00:00',
            'date_to': '2019-04-20 12:00:00',
            'holiday_status_id': self.status.id,
            'employee_id': self.employee1.id,
            'type': 'remove',
        })
        holiday1._compute_warning_range()
        self.assertFalse(holiday1.warning)

        holiday2 = self.env['hr.holidays'].new({
            'date_from': '2019-04-20 10:00:00',
            'date_to': '2019-05-20 12:00:00',
            'holiday_status_id': self.status.id,
            'employee_id': self.employee1.id,
            'type': 'remove',
        })
        holiday2._compute_warning_range()
        self.assertTrue(holiday2.warning)
        self.assertEqual(
            holiday2.warning,
            'Warning: The selected dates are out of'
            ' this holiday type\'s range. (2019-04-01 - 2019-04-30)')
