# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class HrHolidaysMeetingName(TransactionCase):

    def setUp(self):
        super(HrHolidaysMeetingName, self).setUp()
        self.leave_type = self.env.ref('hr_holidays.holiday_status_cl')
        self.leave_obj = self.env['hr.holidays']
        self.employee01 = self.env.ref('hr.employee_root')

    def create_leave(self):
        today = fields.Datetime.now()
        tomorrow = fields.Datetime.to_string(
            datetime.now() + timedelta(days=1))
        leave = self.leave_obj.create({
            'name': 'test',
            'type': 'remove',
            'holiday_type': 'employee',
            'date_from': today,
            'date_to': tomorrow,
            'number_of_days_temp': 1.0,
            'employee_id': self.employee01.id,
            'holiday_status_id': self.leave_type.id,
        })
        return leave

    def test_1(self):
        leave = self.create_leave()
        leave.action_validate()
        self.assertTrue(len(leave.meeting_id) == 1)
        self.assertEqual(leave.meeting_id.name, leave.display_name)

    def test_2(self):
        meeting_description = 'Test meeting name'
        self.leave_type.write({
            'use_leave_name_for_meeting': False,
            'meeting_description': meeting_description
        })
        leave = self.create_leave()
        leave.action_validate()
        self.assertTrue(len(leave.meeting_id) == 1)
        self.assertEqual(leave.meeting_id.name, meeting_description)
