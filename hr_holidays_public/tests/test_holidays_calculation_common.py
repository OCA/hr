# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestHolidaysComputeBase(TransactionCase):
    def setUp(self):
        super(TestHolidaysComputeBase, self).setUp()
        self.HrLeave = self.env["hr.leave"]
        self.HrLeaveType = self.env["hr.leave.type"]
        self.HrHolidaysPublic = self.env["hr.holidays.public"]
        # Remove timezone for controlling data better
        self.env.user.tz = False
        self.calendar = self.env["resource.calendar"].create(
            {
                "name": "Calendar",
                "attendance_ids": [],
            }
        )
        for day in range(5):  # From monday to friday
            self.calendar.attendance_ids = [
                (0, 0, {
                    "name": "Attendance",
                    "dayofweek": str(day),
                    "hour_from": "08",
                    "hour_to": "12",
                }),
                (0, 0, {
                    "name": "Attendance",
                    "dayofweek": str(day),
                    "hour_from": "14",
                    "hour_to": "18",
                }),
            ]
        self.address_uk = self.env["res.partner"].create(
            {
                "name": "Address UK",
                "country_id": self.env.ref("base.uk").id,
            }
        )
        self.address_spain = self.env["res.partner"].create(
            {
                "name": "Address Spain",
                "country_id": self.env.ref("base.es").id,
                "state_id": self.env.ref("base.state_es_cr").id,
            }
        )
        self.employee_1_uk = self.env["hr.employee"].create(
            {
                "name": "Employee 1 UK",
                "resource_calendar_id": self.calendar.id,
                "address_id": self.address_uk.id,
            }
        )
        self.employee_2_spain = self.env["hr.employee"].create(
            {
                "name": "Employee 2 Spain",
                "resource_calendar_id": self.calendar.id,
                "address_id": self.address_spain.id,
            }
        )
        # Use a very old year for avoiding to collapse with current data
        self.public_holiday_global = self.HrHolidaysPublic.create(
            {
                "year": 1946,
                "line_ids": [
                    (0, 0, {"name": "Christmas",
                            "date": "1946-12-25",
                            },
                     ),
                ],
            }
        )
        self.public_holiday_spain = self.HrHolidaysPublic.create(
            {
                "year": 1946,
                "country_id": self.address_spain.country_id.id,
                "line_ids": [
                    (0, 0, {"name": "Before Christmas",
                            "date": "1946-12-24",
                            },
                     ),
                    (0, 0, {"name": "Even More Before Christmas",
                            "date": "1946-12-23",
                            "state_ids": [
                                (6, 0, self.address_spain.state_id.ids),
                            ],
                            },
                     ),
                ],
            }
        )
        self.public_holiday_global_1947 = self.HrHolidaysPublic.create(
            {
                "year": 1947,
                "line_ids": [
                    (0, 0, {"name": "New Eve",
                            "date": "1947-01-01",
                            },
                     ),
                    (0, 0, {"name": "New Eve extended",
                            "date": "1947-01-02",
                            },
                     ),
                ],
            }
        )
