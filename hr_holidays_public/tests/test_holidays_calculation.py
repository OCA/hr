# Copyright 2015 iDT LABS (http://www.@idtlabs.sl)
# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# Copyright 2018 Brainbean Apps
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestHolidaysComputeDaysBase(common.SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super(TestHolidaysComputeDaysBase, cls).setUpClass()
        cls.HrLeave = cls.env['hr.leave']
        cls.HrLeaveType = cls.env['hr.leave.type']
        cls.HrHolidaysPublic = cls.env["hr.holidays.public"]
        # Remove timezone for controlling data better
        cls.env.user.tz = False
        cls.calendar = cls.env['resource.calendar'].create({
            'name': 'Calendar',
            'attendance_ids': [],
        })
        for day in range(5):  # From monday to friday
            cls.calendar.attendance_ids = [
                (0, 0, {
                    'name': 'Attendance',
                    'dayofweek': str(day),
                    'hour_from': '08',
                    'hour_to': '12',
                }),
                (0, 0, {
                    'name': 'Attendance',
                    'dayofweek': str(day),
                    'hour_from': '14',
                    'hour_to': '18',
                }),
            ]
        cls.address_1 = cls.env['res.partner'].create({
            'name': 'Address 1',
            'country_id': cls.env.ref('base.uk').id,
        })
        cls.address_2 = cls.env['res.partner'].create({
            'name': 'Address 1',
            'country_id': cls.env.ref('base.es').id,
            'state_id': cls.env.ref('base.state_es_cr').id,
        })
        cls.employee_1 = cls.env['hr.employee'].create({
            'name': 'Employee 1',
            'resource_calendar_id': cls.calendar.id,
            'address_id': cls.address_1.id,
        })
        cls.employee_2 = cls.env['hr.employee'].create({
            'name': 'Employee 2',
            'resource_calendar_id': cls.calendar.id,
            'address_id': cls.address_2.id,
        })
        # Use a very old year for avoiding to collapse with current data
        cls.public_holiday_global = cls.HrHolidaysPublic.create({
            'year': 1946,
            'line_ids': [
                (0, 0, {
                    'name': 'Christmas',
                    'date': '1946-12-25',
                }),
            ],
        })
        cls.public_holiday_country = cls.HrHolidaysPublic.create({
            'year': 1946,
            'country_id': cls.address_2.country_id.id,
            'line_ids': [
                (0, 0, {
                    'name': 'Before Christmas',
                    'date': '1946-12-24',
                }),
                (0, 0, {
                    'name': 'Even More Before Christmas',
                    'date': '1946-12-23',
                    'state_ids': [
                        (6, 0, cls.address_2.state_id.ids),
                    ]
                }),
            ],
        })

        cls.holiday_type = cls.HrLeaveType.create({
            'name': 'Leave Type Test',
            'exclude_public_holidays': True,
        })
        cls.holiday_type_no_excludes = cls.HrLeaveType.create({
            'name': 'Leave Type Test Without excludes',
            'exclude_public_holidays': False,
        })


class TestHolidaysComputeDays(TestHolidaysComputeDaysBase):
    def test_number_days_excluding_employee_1(self):
        leave_request = self.HrLeave.new({
            'date_from': '1946-12-23 00:00:00',  # Monday
            'date_to': '1946-12-29 23:59:59',  # Sunday
            'holiday_status_id': self.holiday_type.id,
            'employee_id': self.employee_1.id,
        })
        leave_request._onchange_leave_dates()
        self.assertEqual(leave_request.number_of_days, 4)

    def _test_number_days_excluding_employee_2(self):
        leave_request = self.HrLeave.new({
            'date_from': '1946-12-23 00:00:00',  # Monday
            'date_to': '1946-12-29 23:59:59',  # Sunday
            'holiday_status_id': self.holiday_type.id,
            'employee_id': self.employee_2.id,
        })
        leave_request._onchange_leave_dates()
        self.assertEqual(leave_request.number_of_days, 2)

    def test_number_days_not_excluding(self):
        leave_request = self.HrLeave.new({
            'date_from': '1946-12-23 00:00:00',  # Monday
            'date_to': '1946-12-29 23:59:59',  # Sunday
            'holiday_status_id': self.holiday_type_no_excludes.id,
            'employee_id': self.employee_1.id,
        })
        leave_request._onchange_leave_dates()
        self.assertEqual(leave_request.number_of_days, 5)
