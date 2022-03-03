# Copyright 2015 iDT LABS (http://www.@idtlabs.sl)
# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# Copyright 2018 Brainbean Apps
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from .test_holidays_calculation_common import TestHolidaysComputeBase


class TestHolidaysComputeDays(TestHolidaysComputeBase):
    def setUp(self):
        super().setUp()

        self.holiday_type = self.HrLeaveType.create(
            {
                "name": "Leave Type Test",
                "exclude_public_holidays": True,
                "allocation_type": "no",
                "validity_start": "1900-01-01",
            }
        )
        self.holiday_type_no_excludes = self.HrLeaveType.create(
            {
                "name": "Leave Type Test Without excludes",
                "exclude_public_holidays": False,
                "allocation_type": "no",
                "validity_start": "1900-01-01",
            }
        )

    def test_number_days_excluding_employee_1_uk(self):
        leave_request = self.HrLeave.new(
            {
                "date_from": "1946-12-23 00:00:00",  # Monday
                "date_to": "1946-12-29 23:59:59",  # Sunday
                "holiday_status_id": self.holiday_type.id,
                "employee_id": self.employee_1_uk.id,
            }
        )
        leave_request._onchange_leave_dates()
        self.assertEqual(leave_request.number_of_days, 4)

    def _test_number_days_excluding_employee_2_spain(self):
        leave_request = self.HrLeave.new(
            {
                "date_from": "1946-12-23 00:00:00",  # Monday
                "date_to": "1946-12-29 23:59:59",  # Sunday
                "holiday_status_id": self.holiday_type.id,
                "employee_id": self.employee_2_spain.id,
            }
        )
        leave_request._onchange_leave_dates()
        self.assertEqual(leave_request.number_of_days, 2)

    def test_number_days_not_excluding(self):
        leave_request = self.HrLeave.new(
            {
                "date_from": "1946-12-23 00:00:00",  # Monday
                "date_to": "1946-12-29 23:59:59",  # Sunday
                "holiday_status_id": self.holiday_type_no_excludes.id,
                "employee_id": self.employee_1_uk.id,
            }
        )
        leave_request._onchange_leave_dates()
        self.assertEqual(leave_request.number_of_days, 5)

    def test_number_days_across_year(self):
        leave_request = self.HrLeave.new(
            {
                "date_from": "1946-12-23 00:00:00",  # Monday
                "date_to": "1947-01-03 23:59:59",  # Friday
                "holiday_status_id": self.holiday_type.id,
                "employee_id": self.employee_1_uk.id,
            }
        )
        leave_request._onchange_leave_dates()
        self.assertEqual(leave_request.number_of_days, 7)

    def test_number_days_across_year_1_spain(self):
        leave_request = self.HrLeave.new(
            {
                "date_from": "1946-12-23 00:00:00",  # Monday
                "date_to": "1947-01-03 23:59:59",  # Friday
                "holiday_status_id": self.holiday_type.id,
                "employee_id": self.employee_2_spain.id,
            }
        )
        leave_request._onchange_leave_dates()
        self.assertEqual(leave_request.number_of_days, 5)

    def test_number_missing_end(self):
        leave_request = self.HrLeave.new(
            {
                "date_from": "1946-12-23 00:00:00",  # Monday
                "holiday_status_id": self.holiday_type.id,
                "employee_id": self.employee_2_spain.id,
            }
        )
        leave_request._onchange_leave_dates()
        self.assertEqual(leave_request.number_of_days, 0)
