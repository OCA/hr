# -*- coding: utf-8 -*-
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from datetime import datetime, timedelta
from openerp import fields
from openerp.exceptions import ValidationError
from openerp.tests.common import TransactionCase
from openerp.tools.misc import mute_logger


class TestHrAttendance(TransactionCase):

    def setUp(self):
        super(TestHrAttendance, self).setUp()
        self.employee_model = self.env['hr.employee'].with_context(
            action_date=fields.Datetime.to_string(datetime.now())
        )
        # self.test_employee = self.browse_ref('hr.employee_al')
        self.test_employee = self.employee_model.create({
            'name': 'Tester',
            'state': 'absent',
            'rfid_card_code': '5b3f5',
        })
        self.rfid_card_code = '5b3f5'

    def test_valid_employee(self):
        """Valid employee"""
        res = self.employee_model.register_attendance(
            self.rfid_card_code)
        self.assertTrue('action' in res and res['action'] == 'check_in')
        self.assertTrue('logged' in res and res['logged'])
        self.assertTrue(
            'rfid_card_code' in res and
            res['rfid_card_code'] == self.rfid_card_code)
        res = self.employee_model.with_context(
            action_date=fields.Datetime.to_string(
                datetime.now() + timedelta(hours=8)),
        ).register_attendance(
            self.rfid_card_code)
        self.assertTrue('action' in res and res['action'] == 'check_out')
        self.assertTrue('logged' in res and res['logged'])

    @mute_logger('openerp.addons.hr_attendance_rfid.models.hr_employee')
    def test_exception_code(self):
        """Checkout is created for a future datetime"""
        self.env['hr.attendance'].create({
            'employee_id': self.test_employee.id,
            'action': 'sign_in',
        })
        self.test_employee.update({'state': 'present'})
        try:
            res = self.employee_model.register_attendance(
                self.rfid_card_code)
        except ValidationError:
            self.assertNotEquals(res['error_message'], '')

    def test_invalid_code(self):
        """Invalid employee"""
        invalid_code = '029238d'
        res = self.employee_model.register_attendance(invalid_code)
        self.assertTrue('action' in res and res['action'] == 'FALSE')
        self.assertTrue('logged' in res and not res['logged'])
        self.assertTrue(
            'rfid_card_code' in res and
            res['rfid_card_code'] == invalid_code)
