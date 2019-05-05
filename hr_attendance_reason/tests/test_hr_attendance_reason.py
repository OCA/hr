# Copyright 2017 Odoo S.A.
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo.tests.common import TransactionCase
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DF
from datetime import datetime


class TestHrAttendanceReason(TransactionCase):

    def setUp(self):
        super(TestHrAttendanceReason, self).setUp()
        self.att_model = self.env['hr.attendance']
        self.att_reason_model = self.env['hr.attendance.reason']
        self.employee = self.browse_ref('hr.employee_al')
        self.att_reason = self.att_reason_model.create(
            {'name': 'Bus did not come',
             'code': 'BB',
             'action_type': 'sign_in'})

    def test_employee_edit(self):
        att = self.att_model.create(
            {'employee_id': self.employee.id,
             'check_in': datetime.now().strftime(DF)})
        att.write({'attendance_reason_ids': [(4, self.att_reason.id)]})
        self.assertEqual(
            att.attendance_reason_ids.ids, self.att_reason.ids,
            "Bad Attendance Reason")
        self.employee.attendance_action_change()
