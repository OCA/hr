# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from freezegun import freeze_time

from odoo.tests.common import SavepointCase


class TestHours(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.hour_obj = cls.env["hr.employee.hour"]
        cls.test_employee = cls.env["hr.employee"].create({"name": "Jacky"})
        cls.calendar_wednesday_off = cls.env["resource.calendar"].create(
            {
                "name": "35h calendar",
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Monday Morning",
                            "dayofweek": "0",
                            "hour_from": 8,
                            "hour_to": 12,
                            "day_period": "morning",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Monday Evening",
                            "dayofweek": "0",
                            "hour_from": 13,
                            "hour_to": 17,
                            "day_period": "afternoon",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Tuesday Morning",
                            "dayofweek": "1",
                            "hour_from": 8,
                            "hour_to": 12,
                            "day_period": "morning",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Tuesday Evening",
                            "dayofweek": "1",
                            "hour_from": 13,
                            "hour_to": 17,
                            "day_period": "afternoon",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Wednesday Morning",
                            "dayofweek": "2",
                            "hour_from": 8,
                            "hour_to": 12,
                            "day_period": "morning",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Thursday Morning",
                            "dayofweek": "3",
                            "hour_from": 8,
                            "hour_to": 12,
                            "day_period": "morning",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Thursday Evening",
                            "dayofweek": "3",
                            "hour_from": 13,
                            "hour_to": 17,
                            "day_period": "afternoon",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Friday Morning",
                            "dayofweek": "4",
                            "hour_from": 8,
                            "hour_to": 12,
                            "day_period": "morning",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Friday Evening",
                            "dayofweek": "4",
                            "hour_from": 13,
                            "hour_to": 17,
                            "day_period": "afternoon",
                        },
                    ),
                ],
            }
        )
        cls.calendar_wednesday_off._onchange_hours_per_day()
        cls.test_contract_1 = cls.env["hr.contract"].create(
            {
                "name": "Test contract 1",
                "date_start": "2021-12-01",
                "date_end": "2021-12-15",
                "employee_id": cls.test_employee.id,
                "hours_report_last_update": "2021-12-01",
                "wage": 100,
                "state": "open",
                "resource_calendar_id": cls.calendar_wednesday_off.id,
            }
        )
        cls.test_contract_2 = cls.env["hr.contract"].create(
            {
                "name": "Test contract 2",
                "date_start": "2022-01-01",
                "employee_id": cls.test_employee.id,
                "hours_report_last_update": "2022-01-01",
                "wage": 100,
            }
        )

    @freeze_time("2022-02-10")
    def test_contract_dates(self):
        self.assertEqual(
            self.test_employee.hours_report_last_update.strftime("%Y-%m-%d"),
            "2021-12-01",
        )
        self.hour_obj.action_generate_data(employee_ids=self.test_employee.ids)
        self.assertEqual(
            self.test_employee.hours_report_last_update.strftime("%Y-%m-%d"),
            "2022-02-10",
        )

    @freeze_time("2021-12-10")
    def test_create_hours_missing(self):
        self.hour_obj.action_generate_data(employee_ids=self.test_employee.ids)
        hours_missing = self.hour_obj.search(
            [("employee_id", "=", self.test_employee.id)]
        )
        # missing attendance from 01.12.2022 to 10.12.2022 created
        self.assertEqual(len(hours_missing), 7)
        self.assertEqual(sum(hours_missing.mapped("hours_qty")), -48)

    @freeze_time("2021-12-02")
    def test_hours_yesterday_day(self):
        self.hour_obj.action_generate_data(employee_ids=self.test_employee.ids)
        hours_missing = self.hour_obj.search(
            [("employee_id", "=", self.test_employee.id)]
        )
        self.assertEqual(len(hours_missing), 1)
        # wednesday afternoon off
        self.assertEqual(hours_missing.hours_qty, -4)

    @freeze_time("2021-12-01")
    def test_hours_today(self):
        self.hour_obj.action_generate_data(employee_ids=self.test_employee.ids)
        hours_missing = self.hour_obj.search(
            [("employee_id", "=", self.test_employee.id)]
        )
        self.assertEqual(len(hours_missing), 0)

    @freeze_time("2021-12-03")
    def test_hours_today_attendance(self):
        self.env["account.analytic.line"].create(
            {
                "name": "test",
                "date": "2021-12-02",
                "unit_amount": 4,
                "employee_id": self.test_employee.id,
                "project_id": self.env["project.project"].search([], limit=1).id,
            }
        )
        self.hour_obj.action_generate_data(employee_ids=self.test_employee.ids)
        hours = self.hour_obj.search([("employee_id", "=", self.test_employee.id)])

        add = hours.filtered(lambda l: l.sum_type == "add")
        rem = hours.filtered(lambda l: l.sum_type == "remove")
        self.assertEqual(add.hours_qty, 4)
        # 12.01 - 4
        # 12.02 - 8
        self.assertEqual(sum(rem.mapped("hours_qty")), -12)

    def test_hours_today_timesheet_per_contract(self):
        self.assertEqual(self.calendar_wednesday_off.hours_per_day, 7.2)
        with freeze_time("2021-12-31"):
            self.test_contract_1.hours_report_last_update = "2021-12-01"
            aal1 = self.env["account.analytic.line"].create(
                {
                    "name": "test",
                    "date": "2021-12-15",
                    "unit_amount": 2.5,
                    "employee_id": self.test_employee.id,
                    "project_id": self.env["project.project"].search([], limit=1).id,
                }
            )
            self.hour_obj.action_generate_data(employee_ids=self.test_employee.ids)
            atthr_1 = self.hour_obj.search(
                [
                    ("res_id", "=", aal1.id),
                    (
                        "type",
                        "=",
                        "timesheet",
                    ),
                    ("date", "=", "2021-12-15"),
                ]
            )
            contracthr_1 = self.hour_obj.search(
                [
                    ("date", "=", "2021-12-15"),
                    (
                        "type",
                        "=",
                        "contract",
                    ),
                    ("res_id", "=", self.test_contract_1.id),
                ]
            )
        self.assertEqual(
            self.test_contract_1.hours_report_last_update.strftime("%Y-%m-%d"),
            "2021-12-31",
        )
        # we need to disable and enable proper contract as timesheets doesn't
        # have callendar and we use current callendar of the employee
        self.test_contract_1.state = "close"
        self.test_contract_2.state = "open"
        self.test_contract_2.hours_report_last_update = "2021-12-16"
        with freeze_time("2022-02-20"):
            aal2 = self.env["account.analytic.line"].create(
                {
                    "name": "test",
                    "date": "2022-02-09",
                    "unit_amount": 2.5,
                    "employee_id": self.test_employee.id,
                    "project_id": self.env["project.project"].search([], limit=1).id,
                }
            )
            self.hour_obj.action_generate_data(employee_ids=self.test_employee.ids)

        atthr_2 = self.hour_obj.search(
            [
                ("res_id", "=", aal2.id),
                (
                    "type",
                    "=",
                    "timesheet",
                ),
                ("date", "=", "2022-02-09"),
            ]
        )
        contracthr_2 = self.hour_obj.search(
            [
                ("date", "=", "2022-02-09"),
                (
                    "type",
                    "=",
                    "contract",
                ),
                ("res_id", "=", self.test_contract_2.id),
            ]
        )
        self.assertEqual(atthr_1.hours_qty, 2.5)
        # 2.5 / 7.2 - where 7.2 is hours per day
        self.assertAlmostEqual(atthr_1.days_qty, 0.347, 3)
        # 2.5 / 8
        self.assertEqual(atthr_2.hours_qty, 2.5)
        self.assertEqual(atthr_2.days_qty, 0.3125)

        # morning only
        self.assertEqual(contracthr_1.hours_qty, -4)
        self.assertEqual(contracthr_1.days_qty, -0.5)
        # whole day
        self.assertEqual(contracthr_2.hours_qty, -8)
        self.assertEqual(contracthr_2.days_qty, -1)

    # # TODO extra work day
    # # TODO timesheet for weekday
