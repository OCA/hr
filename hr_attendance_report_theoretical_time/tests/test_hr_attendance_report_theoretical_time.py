# Copyright 2017-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestHrAttendanceReportTheoreticalTime(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.HrLeave = cls.env['hr.leave']
        cls.HrHolidaysPublic = cls.env["hr.holidays.public"]
        cls.HrLeaveType = cls.env["hr.leave.type"]
        cls.calendar = cls.env['resource.calendar'].create({
            'name': 'Test Calendar',
            'attendance_ids': False,
            'tz': 'UTC',
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
        cls.leave_type = cls.HrLeaveType.create({
            'name': 'Leave Type Test',
            'exclude_public_holidays': True,
            'allocation_type': 'no',
            'validity_start': False,
        })
        # Remove timezone for controlling data better
        cls.env.user.tz = False
        # Force employee create_date for having auto-generated report entries
        cls.env.cr.execute(
            "UPDATE hr_employee SET create_date = %s "
            "WHERE id in %s", (
                '1946-12-23 12:00:00',
                (cls.employee_1.id, cls.employee_2.id),
            ),
        )
        # Leave for employee 1
        cls.leave = cls.HrLeave.create({
            'date_from': '1946-12-26 00:00:00',
            'date_to': '1946-12-26 23:59:59',
            'request_date_from': '1946-12-26',
            'request_date_to': '1946-12-26',
            'employee_id': cls.employee_1.id,
            'holiday_status_id': cls.leave_type.id,
        })
        cls.leave._onchange_request_parameters()
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

    def test_theoretical_hours_recompute(self):
        """Change calendar, and then recompute with the wizard"""
        # Get rid of 4 hours per day so the theoretical should be 4.
        self.calendar.attendance_ids.filtered(
            lambda x: x.hour_from == 14.0).unlink()
        # The attendances theoretical hours remain at 8 if not recomputed
        self.assertEqual(self.attendances[0].theoretical_hours, 8)
        self.assertEqual(self.attendances[1].theoretical_hours, 8)
        # Then we run the wizard just for day 23
        wizard = self.env['recompute.theoretical.attendance'].create({
            'employee_ids': [(4, self.employee_1.id)],
            'date_from': '1946-12-23 00:00:00',
            'date_to': '1946-12-23 23:59:59',
        })
        wizard.action_recompute()
        # Attendances for day 23 are recomputed
        self.assertEqual(self.attendances[0].theoretical_hours, 4)
        self.assertEqual(self.attendances[1].theoretical_hours, 4)
        # Attendances for day 24 remaine as they were
        self.assertEqual(self.attendances[2].theoretical_hours, 8)
        self.assertEqual(self.attendances[3].theoretical_hours, 8)

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

    def test_wizard_theoretical_time(self):
        department = self.env['hr.department'].create({'name': 'Department'})
        tag = self.env['hr.employee.category'].create({'name': 'Tag'})
        self.employee_1.write({
            'department_id': department.id,
            'category_ids': [(4, tag.id)],
        })
        wizard = self.env['wizard.theoretical.time'].create({
            'department_id': department.id,
            'category_ids': [(4, tag.id)],
        })
        wizard.populate()
        report = wizard.view_report()
        self.assertTrue(wizard.employee_ids)
        self.assertEqual(wizard.employee_ids[0].name, self.employee_1.name)
        self.assertEqual(
            report['domain'],
            [('employee_id', 'in', [self.employee_1.id])]
        )
