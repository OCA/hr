# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from odoo.tests.common import TransactionCase
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DF
from datetime import datetime


class TestHrAttendanceReason(TransactionCase):

    def setUp(self):
        super(TestHrAttendanceReason, self).setUp()
        self.hr_attendance = self.env['hr.attendance']
        self.employee = self.env['hr.employee'].create({
            'name': 'Employee'
        })

    def test_employee_edit(self):
        dti = datetime.now()
        dto = datetime.now() + relativedelta(hours=7)
        att = self.hr_attendance.create(
            {'employee_id': self.employee.id,
             'check_in': dti.strftime(DF),
             'check_out': dto.strftime(DF),
             })
        self.assertEqual(att.open_worked_hours, 7.0, "Wrong hours")
        dt = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0) - relativedelta(
            hours=15)
        att = self.hr_attendance.create(
            {'employee_id': self.employee.id,
             'check_in': dt.strftime(DF),
             })
        self.hr_attendance.check_for_incomplete_attendances()
        self.assertEqual(att.worked_hours, 11.0, "Attendance not closed")
        reason = self.env['hr.attendance.reason'].search(
            [('code', '=', 'S-CO')], limit=1)
        reason.unlink()
        dti += relativedelta(hours=10)
        dto += relativedelta(hours=10)
        att2 = self.hr_attendance.create(
            {'employee_id': self.employee.id,
             'check_in': dti.strftime(DF),
             'check_out': dto.strftime(DF),
             })
        self.hr_attendance.check_for_incomplete_attendances()
        self.assertFalse(att2.attendance_reason_ids)
