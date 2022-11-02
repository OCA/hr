# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .test_holidays_calculation_common import TestHolidaysComputeBase


class TestHolidaysCompute(TestHolidaysComputeBase):
    def setUp(self):
        super().setUp()

        self.holiday_type_in_hours = self.HrLeaveType.create(
            {
                "name": "Leave Type in hours",
                "exclude_public_holidays": True,
                "request_unit": "hour",
                "allocation_type": "no",
                "validity_start": "1900-01-01",
            }
        )
        self.holiday_type_no_excludes_in_hours = self.HrLeaveType.create(
            {
                "name": "Leave Type in hours Without excludes",
                "exclude_public_holidays": False,
                "request_unit": "hour",
                "allocation_type": "no",
                "validity_start": "1900-01-01",
            }
        )

    def test_number_hours_excluding_employee_1_uk(self):
        leave_request = self.HrLeave.new(
            {
                "date_from": "1946-12-23 00:00:00",  # Monday
                "date_to": "1946-12-29 23:59:59",  # Sunday
                "holiday_status_id": self.holiday_type_in_hours.id,
                "employee_id": self.employee_1_uk.id,
            }
        )
        leave_request._onchange_leave_dates()

        # Exclude dec 25 wich is public holidays
        # We must have 4 days of work -> 4 * 8 hours = 32 hours
        self.assertEqual(leave_request.number_of_days, 4)
        self.assertEqual(leave_request.number_of_hours_display, 4 * 8)

    def test_number_hours_not_excluding(self):
        leave_request = self.HrLeave.new(
            {
                "date_from": "1946-12-23 00:00:00",  # Monday
                "date_to": "1946-12-29 23:59:59",  # Sunday
                "holiday_status_id": self.holiday_type_no_excludes_in_hours.id,
                "employee_id": self.employee_1_uk.id,
            }
        )
        leave_request._onchange_leave_dates()
        # Don't exclude dec 25 wich is public holidays
        # We must have 5 days of work -> 5 * 8 hours = 40 hours
        self.assertEqual(leave_request.number_of_days, 5)
        self.assertEqual(leave_request.number_of_hours_display, 5 * 8)

    def test_number_hours_on_public_holiday(self):
        leave_request = self.HrLeave.new(
            {
                "date_from": "1946-12-25 00:00:00",
                "date_to": "1946-12-25 23:59:59",
                "holiday_status_id": self.holiday_type_in_hours.id,
                "employee_id": self.employee_1_uk.id,
            }
        )
        leave_request._onchange_leave_dates()
        # Compute only on public holiday, result must be 0 hours
        self.assertEqual(leave_request.number_of_hours_display, 0)

    def test_number_hours_on_part_of_a_working_day(self):
        leave_request = self.HrLeave.new(
            {
                "date_from": "1946-12-23 11:00:00",
                "date_to": "1946-12-23 18:00:00",
                "holiday_status_id": self.holiday_type_in_hours.id,
                "employee_id": self.employee_1_uk.id,
            }
        )
        leave_request._onchange_leave_dates()
        # 11h to 12h + 14h to 18h = 5h
        self.assertEqual(leave_request.number_of_hours_display, 5)

    def test_number_of_hours_excluding_employee_2_spain(self):
        leave_request = self.HrLeave.create(
            {
                "date_from": "1946-12-23 00:00:00",  # Monday
                "date_to": "1946-12-29 23:59:59",  # Sunday
                "holiday_status_id": self.holiday_type_in_hours.id,
                "employee_id": self.employee_2_spain.id,
            }
        )
        leave_request._onchange_leave_dates()
        # Off 23,24,25 = 5 - 3 days = 2 days * 8h = 16h
        self.assertEqual(leave_request.number_of_days, 2)
        self.assertEqual(leave_request.number_of_hours_display, 16)

        # Must be the same after validation
        leave_request.action_validate()
        self.assertEqual(leave_request.number_of_days, 2)
        self.assertEqual(leave_request.number_of_hours_display, 16)

    def test_in_hours_number_missing_start(self):
        leave_request = self.HrLeave.new(
            {
                "date_to": "1946-12-23 00:00:00",  # Monday
                "holiday_status_id": self.holiday_type_in_hours.id,
                "employee_id": self.employee_2_spain.id,
            }
        )
        leave_request._onchange_leave_dates()
        self.assertEqual(leave_request.number_of_days, 0)
        self.assertEqual(leave_request.number_of_hours_display, 0)
