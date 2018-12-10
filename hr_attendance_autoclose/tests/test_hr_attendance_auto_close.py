# -*- coding: utf-8 -*-
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from odoo.tests.common import TransactionCase
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DF
from datetime import datetime


class TestHrAttendanceReason(TransactionCase):

    def setUp(self):
        super(TestHrAttendanceReason, self).setUp()
        self.att_model = self.env['hr.attendance']
        self.employee = self.browse_ref('hr.employee_al')

    def test_employee_edit(self):
        dti = datetime.now()
        dto = datetime.now() + relativedelta(hours=7)
        att = self.att_model.create(
            {'employee_id': self.employee.id,
             'check_in': dti.strftime(DF),
             'check_out': dto.strftime(DF),
             })
        self.assertEqual(att.open_worked_hours, 7.0, "Wrong hours")
        dt = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0) - relativedelta(
            hours=15)
        att = self.att_model.create(
            {'employee_id': self.employee.id,
             'check_in': dt.strftime(DF),
             })
        self.att_model.check_for_incomplete_attendances()
        self.assertEqual(att.worked_hours, 11.0, "Attendance not closed")
