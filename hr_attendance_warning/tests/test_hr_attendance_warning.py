import odoo.tests.common as common
from odoo import fields
from mock import patch
from datetime import timedelta


class TestHrAttendanceWarning(common.TransactionCase):

    def setUp(self):
        super(TestHrAttendanceWarning, self).setUp()

        self.calendar = self.env['resource.calendar'].create({
            'name': 'Calendar 1',
            'attendance_ids': []
        })

        for i in range(0, 7):
            self.env['resource.calendar.attendance'].create({
                'name': 'Day ' + str(i),
                'dayofweek': str(i),
                'hour_from': 8.0,
                'hour_to': 16.0,
                'margin_from': 30,
                'margin_to': 30,
                'calendar_id': self.calendar.id,
            })

        self.employee = self.env['hr.employee'].create({
            'name': 'Employee',
            'resource_calendar_id': self.calendar.id
        })

    def test_out_of_interval(self):
        with patch('odoo.fields.Datetime.now') as p:
            p.return_value = '2018-06-15 12:00:00'
            self.employee.attendance_action_change()
            att = self.env['hr.attendance'].search(
                [('employee_id', '=', self.employee.id)], limit=1)
            warning = self.env['hr.attendance.warning'].search(
                [('employee_id', '=', self.employee.id)], limit=1)
            self.assertFalse(warning)
            self.assertTrue(att)

            p.return_value = '2018-06-15 19:00:00'
            self.employee.attendance_action_change()
            warning = self.env['hr.attendance.warning'].search(
                [('employee_id', '=', self.employee.id)], limit=1)
            warning_line = self.env['hr.attendance.warning.line'].search(
                [('warning_id', '=', warning.id)], limit=1)
            self.assertTrue(warning)
            self.assertEqual(warning.employee_id, self.employee)
            self.assertEqual(warning_line.warning_type, 'out_of_interval')

    def test_out_of_interval_holidays(self):
        with patch('odoo.fields.Datetime.now') as now,\
                patch('odoo.fields.Date.today') as today:
            now.return_value = '2018-06-15 12:00:00'
            today.return_value = '2018-06-15'

            holiday_start = fields.Datetime.to_string(
                fields.Date.from_string(fields.Date.today())
                - timedelta(days=1))
            holiday_end = fields.Datetime.to_string(
                fields.Date.from_string(fields.Date.today())
                + timedelta(days=1))

            status_1 = self.env['hr.holidays.status'].create({
                'name': 'Status 1',
                'limit': True,
            })
            self.env['hr.holidays'].create({
                'name': 'Allocation Request 1',
                'holiday_status_id': status_1.id,
                'holiday_type': 'employee',
                'employee_id': self.employee.id,
                'number_of_days_temp': 10,
                'type': 'add',
            })
            leave_1 = self.env['hr.holidays'].create({
                'holiday_status_id': status_1.id,
                'holiday_type': 'employee',
                'type': 'remove',
                'date_from': holiday_start,
                'date_to': holiday_end,
                'employee_id': self.employee.id,
            })
            leave_1.action_approve()
            self.employee.attendance_action_change()
            warning = self.env['hr.attendance.warning'].search(
                [('employee_id', '=', self.employee.id)], limit=1)
            warning_line = self.env['hr.attendance.warning.line'].search(
                [('warning_id', '=', warning.id)], limit=1)
            self.assertTrue(warning)

            self.assertEqual(warning.employee_id, self.employee)
            self.assertEqual(warning_line.warning_type, 'out_of_interval')
            warning_line._compute_message()
            warning._compute_message_preview()
            self.assertEqual(
                warning_line.message, 'Came to work out of working hours.'
            )
            self.assertEqual(
                warning.message_preview, 'Came to work out of working hours.'
            )
            warning._compute_day_date()
            date_t = fields.Datetime.from_string(warning.day_date)
            date = fields.Date.to_string(date_t)
            self.assertEqual(warning.day_date, date)

            count = self.env['hr.attendance.warning'].pending_warnings_count()
            self.assertEqual(len(count), 1)

            self.env['hr.attendance.warning.solve'].with_context(
                active_ids=[warning.id]
            ).solve_warnings()
            self.assertEqual(warning.state, 'solved')

            warning.open_employee_attendances()

    def test_no_check_in_out(self):
        with patch('odoo.fields.Datetime.now') as now,\
                patch('odoo.fields.Date.today') as today:
            now.return_value = '2018-06-11 21:00:00'
            today.return_value = '2018-06-11'
            attendances = self.env['resource.calendar.attendance'].search(
                [('calendar_id', '=', self.calendar.id)])
            for att in attendances:
                self.assertFalse(att.next_check_from)
                self.assertFalse(att.next_check_to)

            monday = self.env['resource.calendar.attendance'].search(
                [('calendar_id', '=', self.calendar.id),
                 ('dayofweek', '=', 0)], limit=1)
            self.env['resource.calendar.attendance'].cron_attendance_checks()

            self.assertEqual(fields.Datetime.to_string(
                fields.Datetime.context_timestamp(
                    monday,
                    fields.Datetime.from_string(monday.next_check_from)
                )), '2018-06-11 08:30:00')
            self.assertEqual(fields.Datetime.to_string(
                fields.Datetime.context_timestamp(
                    monday,
                    fields.Datetime.from_string(monday.next_check_to)
                )), '2018-06-11 16:30:00')

            tuesday = self.env['resource.calendar.attendance'].search(
                [('calendar_id', '=', self.calendar.id),
                 ('dayofweek', '=', 1)], limit=1)

            self.assertEqual(fields.Datetime.to_string(
                fields.Datetime.context_timestamp(
                    tuesday,
                    fields.Datetime.from_string(tuesday.next_check_from)
                )), '2018-06-12 08:30:00')
            self.assertEqual(fields.Datetime.to_string(
                fields.Datetime.context_timestamp(
                    tuesday,
                    fields.Datetime.from_string(tuesday.next_check_to)
                )), '2018-06-12 16:30:00')

            self.env['resource.calendar.attendance'].cron_attendance_checks()

            warning_in = self.env['hr.attendance.warning'].search(
                [('employee_id', '=', self.employee.id)], limit=1)
            warning_line = self.env['hr.attendance.warning.line'].search(
                [('warning_id', '=', warning_in.id)], limit=1)
            self.assertTrue(warning_line)
            self.assertEqual(warning_line.warning_type, 'no_check_in')
            warning_line._compute_message()
            self.assertEqual(
                warning_line.message, 'Didn\'t check in between "2018-06-11'
                                      ' 07:30:00" and "2018-06-11 08:30:00".')

            warning_in.pending2solved()
            self.assertEqual(warning_in.state, 'solved')
            warning_in.solved2pending()
            self.assertEqual(warning_in.state, 'pending')

            monday.write({'margin_to': False})
            monday._onchange_to()

            monday._check_issue_end(fields.Datetime.now())
            self.env['resource.calendar.attendance'].cron_attendance_checks()

            warning_out = self.env['hr.attendance.warning.line'].search(
                [('employee_id', '=', self.employee.id),
                 ('warning_type', '=', 'no_check_out')])

            self.assertEqual(len(warning_out), 1)
            warning_out._compute_message()
            self.assertEqual(
                warning_out.message, 'Didn\'t check out between "2018-06-11 '
                                     '15:30:00" and "2018-06-11 16:30:00".')

            monday.margin_from = 1
            monday._onchange_from()
            self.assertEqual(fields.Datetime.to_string(
                fields.Datetime.context_timestamp(
                    monday,
                    fields.Datetime.from_string(monday.next_check_from)
                )), '2018-06-11 08:01:00')

            monday.margin_to = 1
            monday._onchange_to()
            self.assertEqual(fields.Datetime.to_string(
                fields.Datetime.context_timestamp(
                    monday,
                    fields.Datetime.from_string(monday.next_check_to)
                )), '2018-06-11 16:01:00')

            self.employee.write({'active': False})
            self.employee._create_warning('no_check_out', '2018-06-11')
            warning_out = self.env['hr.attendance.warning.line'].search(
                [('employee_id', '=', self.employee.id),
                 ('warning_type', '=', 'no_check_out')])

            self.assertEqual(len(warning_out), 1)

    def test_no_check_in_out_holidays(self):
        with patch('odoo.fields.Datetime.now') as now,\
                patch('odoo.fields.Date.today') as today:
            now.return_value = '2018-06-15 12:00:00'
            today.return_value = '2018-06-15'

            holiday_start = fields.Datetime.to_string(
                fields.Date.from_string(fields.Date.today())
                - timedelta(days=1))
            holiday_end = fields.Datetime.to_string(
                fields.Date.from_string(fields.Date.today())
                + timedelta(days=1))

            status_1 = self.env['hr.holidays.status'].create({
                'name': 'Status 1',
                'limit': True,
            })
            self.env['hr.holidays'].create({
                'name': 'Allocation Request 1',
                'holiday_status_id': status_1.id,
                'holiday_type': 'employee',
                'employee_id': self.employee.id,
                'number_of_days_temp': 10,
                'type': 'add',
            })
            leave_1 = self.env['hr.holidays'].create({
                'holiday_status_id': status_1.id,
                'holiday_type': 'employee',
                'type': 'remove',
                'date_from': holiday_start,
                'date_to': holiday_end,
                'employee_id': self.employee.id,
            })
            leave_1.action_approve()
            self.env['resource.calendar.attendance'].cron_attendance_checks()
            self.env['resource.calendar.attendance'].cron_attendance_checks()
            warning_in = self.env['hr.attendance.warning'].search(
                [('employee_id', '=', self.employee.id)], limit=1)
            self.assertFalse(warning_in)

    def test_public_holidays(self):
        self.env['hr.holidays.public'].create({
            'year': 2018,
            'line_ids': [(0, 0, {'date': '2018-06-15', 'name': 'Name'})]
        })
        with patch('odoo.fields.Datetime.now') as now,\
                patch('odoo.fields.Date.today') as today:
            now.return_value = '2018-06-15 10:00:00'
            today.return_value = '2018-06-15'

            self.env['resource.calendar.attendance'].cron_attendance_checks()
            self.env['resource.calendar.attendance'].cron_attendance_checks()
            warnings = self.env['hr.attendance.warning'].search(
                [('employee_id', '=', self.employee.id)], limit=1)
            self.assertFalse(warnings)

            self.employee.attendance_action_change()
            warnings = self.env['hr.attendance.warning'].search(
                [('employee_id', '=', self.employee.id)], limit=1)
            self.assertTrue(warnings)
