# -*- coding: utf-8 -*-
# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.hr_holidays_compute_days.tests.test_holidays_compute_days \
    import TestHolidaysComputeDaysBase


class TestHrAttendanceReportTheoreticalTime(TestHolidaysComputeDaysBase):
    @classmethod
    def setUpClass(cls):
        super(TestHrAttendanceReportTheoreticalTime, cls).setUpClass()
        # Force employee create_date for having auto-generated report entries
        cls.env.cr.execute(
            "UPDATE hr_employee SET create_date = %s "
            "WHERE id in %s", (
                '1946-12-23 12:00:00',
                (cls.employee_1.id, cls.employee_2.id),
            ),
        )
        # Leave for employee 1
        cls.leave = cls.env['hr.holidays'].create({
            'date_from': '1946-12-26 08:00:00',
            'date_to': '1946-12-26 18:00:00',
            'employee_id': cls.employee_1.id,
            'holiday_status_id': cls.holiday_type.id,
            'state': 'confirm',
        })
        cls.leave.action_validate()
        cls.attendances = []
        for employee in (cls.employee_1, cls.employee_2):
            for day in range(23, 27):
                cls.attendances.append(cls.env['hr.attendance'].create({
                    'employee_id': employee.id,
                    'check_in': '1946-12-%s 08:00:00' % day,
                    'check_out': '1946-12-%s 12:00:00' % day,
                }))
                cls.attendances.append(cls.env['hr.attendance'].create({
                    'employee_id': employee.id,
                    'check_in': '1946-12-%s 14:00:00' % day,
                    'check_out': '1946-12-%s 18:00:00' % day,
                }))

    def test_theoretical_hours(self):
        # EMPLOYEE 1
        # 1946-12-23
        self.assertEqual(self.attendances[0].theoretical_hours, 8)
        self.assertEqual(self.attendances[1].theoretical_hours, 8)
        # 1946-12-24
        self.assertEqual(self.attendances[2].theoretical_hours, 8)
        self.assertEqual(self.attendances[3].theoretical_hours, 8)
        # 1946-12-25 - Global public holiday
        self.assertEqual(self.attendances[4].theoretical_hours, 0)
        self.assertEqual(self.attendances[5].theoretical_hours, 0)
        # 1946-12-26
        self.assertEqual(self.attendances[6].theoretical_hours, 0)
        self.assertEqual(self.attendances[7].theoretical_hours, 0)
        # EMPLOYEE 2
        # 1946-12-23 - Public holidays for state of employee 2
        self.assertEqual(self.attendances[8].theoretical_hours, 0)
        self.assertEqual(self.attendances[9].theoretical_hours, 0)
        # 1946-12-24 - Public holiday for country of employee 2
        self.assertEqual(self.attendances[10].theoretical_hours, 0)
        self.assertEqual(self.attendances[11].theoretical_hours, 0)
        # 1946-12-25 - Global public holiday
        self.assertEqual(self.attendances[12].theoretical_hours, 0)
        self.assertEqual(self.attendances[13].theoretical_hours, 0)
        # 1946-12-26 - Employee 2 leave
        self.assertEqual(self.attendances[14].theoretical_hours, 8)
        self.assertEqual(self.attendances[15].theoretical_hours, 8)

    def test_hr_attendance_read_group(self):
        # TODO: Test when having theoretical_hours_start_date set
        # Group by employee
        res = self.env['hr.attendance.theoretical.time.report'].read_group(
            [('date', '>=', '1946-12-23'),
             ('date', '<', '1946-12-31'),
             ('employee_id', 'in', (self.employee_1.id, self.employee_2.id))],
            ['employee_id', 'theoretical_hours', 'worked_hours', 'difference'],
            ['employee_id'],
        )
        # It should include 4 working days (25 is holiday and 26 is leave)
        self.assertEqual(res[0]['theoretical_hours'], 32)
        self.assertEqual(res[0]['worked_hours'], 32)
        self.assertEqual(res[0]['difference'], 0)
        # It should include 5 working days (25 is holiday)
        self.assertEqual(res[1]['theoretical_hours'], 24)
        self.assertEqual(res[1]['worked_hours'], 32)
        self.assertEqual(res[1]['difference'], 8)
        # Group by day
        res = self.env['hr.attendance.theoretical.time.report'].read_group(
            [('date', '>=', '1946-12-23'),
             ('date', '<', '1946-12-31'),
             ('employee_id', '=', self.employee_1.id)],
            ['employee_id', 'theoretical_hours', 'date'],
            ['date:day'],
        )
        self.assertEqual(res[0]['theoretical_hours'], 8)  # 1946-12-23
        self.assertEqual(res[1]['theoretical_hours'], 8)  # 1946-12-24
        self.assertEqual(res[2]['theoretical_hours'], 0)  # 1946-12-25
        self.assertEqual(res[3]['theoretical_hours'], 0)  # 1946-12-26
        self.assertEqual(res[4]['theoretical_hours'], 8)  # 1946-12-27(virtual)
        self.assertEqual(res[5]['theoretical_hours'], 8)  # 1946-12-30(virtual)

    def test_change_hr_holidays_public(self):
        self.public_holiday_global.line_ids[0].write({
            'date': '1946-12-23',
        })
        # 1946-12-23
        self.assertEqual(self.attendances[0].theoretical_hours, 0)
        self.assertEqual(self.attendances[8].theoretical_hours, 0)
        # 1946-12-25
        self.assertEqual(self.attendances[4].theoretical_hours, 8)
        self.assertEqual(self.attendances[12].theoretical_hours, 8)

    def test_change_hr_holidays(self):
        self.leave.action_refuse()
        # 1946-12-26 - Employee 2
        self.assertEqual(self.attendances[14].theoretical_hours, 8)

    def test_hr_holidays_status_include_in_theoretical(self):
        obj = self.env['hr.attendance.theoretical.time.report']
        self.leave.holiday_status_id.include_in_theoretical = True
        # 1946-12-26 - Employee 1
        a = self.attendances[6]
        self.assertEqual(obj._theoretical_hours(a.employee_id, a.check_in), 8)
