# Copyright 2019 ForgeFlow, S.L.
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo.tests.common import TransactionCase


class TestHrAttendanceGeolocation(TransactionCase):
    def setUp(self):
        super(TestHrAttendanceGeolocation, self).setUp()
        self.hr_attendance_model = self.env["hr.attendance"]
        self.hr_employee_model = self.env["hr.employee"]
        self.employee = self.hr_employee_model.create({"name": "Employee A"})
        self.location = ["41.3910970", "2.1548569"]

    def test_attendance_geolocation(self):
        # Called from js
        self.employee.attendance_manual(
            "hr_attendance.hr_attendance_action_my_attendances", None, self.location
        )
        attendances = self.hr_attendance_model.search(
            [("employee_id", "=", self.employee.id)]
        )
        self.assertEqual(len(attendances), 1, "One attendance should have been created")
        self.assertEqual(attendances[0].check_in_latitude, float(self.location[0]))
        self.assertEqual(attendances[0].check_in_longitude, float(self.location[1]))
