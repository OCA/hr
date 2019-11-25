# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo.tests.common import TransactionCase
from odoo import exceptions


class TestHrAttendancePermittedGeolocation(TransactionCase):

    def setUp(self):
        super(TestHrAttendancePermittedGeolocation, self).setUp()
        self.hr_attendance_model = self.env['hr.attendance']
        self.hr_employee_model = self.env['hr.employee']
        self.hr_attendance_location_model = self.env['hr.attendance.location']
        self.employee = self.hr_employee_model.create({
            'name': 'Employee A',
        })
        self.location_in = self.hr_attendance_location_model.create({
            'name': 'Permitted Location 1 (in range)',
            'latitude': 41.3910970,
            'longitude': 2.1548569,
            'allowed_radius': 1,
        })
        self.location_out = self.hr_attendance_location_model.create({
            'name': 'Permitted Location 2 (out of range)',
            'latitude': 2.1548569,
            'longitude': 41.3910970,
            'allowed_radius': 1,
        })
        self.attendance_location = [41.3910970, 2.1548569]

    def test_permitted_geolocation_allow(self):
        # Called from js
        self.employee.attendance_manual(
            'hr_attendance.hr_attendance_action_my_attendances', None,
            self.attendance_location
        )
        attendances = self.hr_attendance_model.search([
            ('employee_id', '=', self.employee.id)])
        self.assertEqual(
            len(attendances), 1, "One attendance should have been created")

    def test_permitted_geolocation_2_deny(self):
        # We archive the Location in range
        self.location_in.write({
            'active': False,
        })
        with self.assertRaises(exceptions.ValidationError):
            # Called from js
            self.employee.attendance_manual(
                'hr_attendance.hr_attendance_action_my_attendances', None,
                self.attendance_location
            )
        attendances = self.hr_attendance_model.search([
            ('employee_id', '=', self.employee.id)])
        self.assertEqual(
            len(attendances), 0, "No attendances should have been created")
