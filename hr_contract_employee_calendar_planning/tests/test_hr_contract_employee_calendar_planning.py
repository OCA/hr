# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import Command, fields
from odoo.tools import mute_logger

from odoo.addons.hr_employee_calendar_planning.tests import (
    test_hr_employee_calendar_planning,
)

from ..hooks import post_init_hook


class TestHrContractEmployeeCalendarPlanning(
    test_hr_employee_calendar_planning.TestHrEmployeeCalendarPlanningCommon
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee.calendar_ids = [
            Command.create(
                {"date_start": "2019-12-31", "calendar_id": cls.calendar1.id}
            ),
        ]
        cls.contract_1 = cls.env["hr.contract"].create(
            {
                "name": "Test contract1",
                "wage": 1,
                "state": "close",
                "employee_id": cls.employee.id,
                "date_start": "2018-11-30",
                "date_end": "2019-11-30",
                "resource_calendar_id": cls.employee.resource_calendar_id.id,
            }
        )
        cls.contract_2 = cls.env["hr.contract"].create(
            {
                "name": "Test contract2",
                "wage": 1,
                "state": "open",
                "employee_id": cls.employee.id,
                "date_start": "2019-12-01",
                "resource_calendar_id": cls.employee.resource_calendar_id.id,
            }
        )

    @mute_logger("odoo.models.unlink")
    def test_change_employee_calendar(self):
        old_calendar = self.employee.resource_calendar_id
        self.employee.calendar_ids.filtered(
            lambda x: x.calendar_id == self.calendar1
        ).write({"date_end": "2019-12-31"})
        self.employee.calendar_ids = [
            Command.create(
                {"date_start": "2020-01-01", "calendar_id": self.calendar2.id}
            ),
        ]
        self.assertEqual(self.contract_1.resource_calendar_id, old_calendar)
        self.assertEqual(
            self.contract_2.resource_calendar_id, self.employee.resource_calendar_id
        )

    @mute_logger("odoo.models.unlink")
    def test_calendar_migration_from_contracts_01(self):
        # date_start from contract1 to avoid overlapping log
        self.employee.calendar_ids.filtered(
            lambda x: x.calendar_id == self.calendar1
        ).write({"date_start": "2018-11-30"})
        self.assertEqual(len(self.employee.calendar_ids), 1)
        # Force to incorrect calendar to contracts
        self.env.cr.execute(
            f"UPDATE hr_contract SET resource_calendar_id = {self.calendar1.id} WHERE id = {self.contract_1.id}"  # noqa: E501
        )
        self.contract_1.invalidate_recordset(["resource_calendar_id"])
        self.env.cr.execute(
            f"UPDATE hr_contract SET resource_calendar_id = {self.calendar2.id} WHERE id = {self.contract_2.id}"  # noqa: E501
        )
        self.contract_2.invalidate_recordset(["resource_calendar_id"])
        # calendar migration from contracts
        old_calendars = self.employee.calendar_ids
        post_init_hook(self.env)
        self.assertEqual(len(self.employee.calendar_ids), 2)
        self.assertEqual(old_calendars.calendar_id, self.calendar1)
        self.assertEqual(
            old_calendars.date_start, fields.Date.from_string("2018-11-30")
        )
        self.assertEqual(old_calendars.date_end, fields.Date.from_string("2019-11-30"))
        new_calendars = self.employee.calendar_ids - old_calendars
        self.assertEqual(len(new_calendars), 1)
        self.assertEqual(new_calendars.calendar_id, self.calendar2)
        self.assertEqual(
            new_calendars.date_start, fields.Date.from_string("2019-12-01")
        )
        self.assertFalse(new_calendars.date_end)

    @mute_logger("odoo.models.unlink")
    def test_calendar_migration_from_contracts_02(self):
        # set calendar to before contract dates
        self.employee.calendar_ids.filtered(
            lambda x: x.calendar_id == self.calendar1
        ).write({"date_start": False, "date_end": "2018-11-29"})
        self.assertEqual(len(self.employee.calendar_ids), 1)
        # Force to incorrect calendar to contracts
        self.env.cr.execute(
            f"UPDATE hr_contract SET resource_calendar_id = {self.calendar1.id} WHERE id = {self.contract_1.id}"  # noqa: E501
        )
        self.contract_1.invalidate_recordset(["resource_calendar_id"])
        self.env.cr.execute(
            f"UPDATE hr_contract SET resource_calendar_id = {self.calendar2.id} WHERE id = {self.contract_2.id}"  # noqa: E501
        )
        self.contract_2.invalidate_recordset(["resource_calendar_id"])
        # calendar migration from contracts
        old_calendars = self.employee.calendar_ids
        post_init_hook(self.env)
        self.assertEqual(len(self.employee.calendar_ids), 3)
        self.assertEqual(old_calendars.calendar_id, self.calendar1)
        self.assertFalse(old_calendars.date_start)
        self.assertEqual(old_calendars.date_end, fields.Date.from_string("2018-11-29"))
        new_calendars = self.employee.calendar_ids - old_calendars
        self.assertEqual(len(new_calendars), 2)
        new_calendars_1 = new_calendars.filtered(
            lambda x: x.calendar_id == self.calendar1
        )
        self.assertEqual(len(new_calendars_1), 1)
        self.assertEqual(
            new_calendars_1.date_start, fields.Date.from_string("2018-11-30")
        )
        self.assertEqual(
            new_calendars_1.date_end, fields.Date.from_string("2019-11-30")
        )
        new_calendars_2 = new_calendars.filtered(
            lambda x: x.calendar_id == self.calendar2
        )
        self.assertEqual(len(new_calendars_2), 1)
        self.assertEqual(
            new_calendars_2.date_start, fields.Date.from_string("2019-12-01")
        )
        self.assertFalse(new_calendars_2.date_end)

    def test_contract_create_write(self):
        self.contract_2.write(
            {
                "state": "close",
                "date_end": "2019-12-31",
            }
        )
        contract = self.env["hr.contract"].create(
            {
                "name": "Test open contract",
                "wage": 1,
                "state": "open",
                "employee_id": self.employee.id,
                "date_start": "2020-01-01",
                "resource_calendar_id": self.calendar2.id,
            }
        )
        self.assertNotEqual(self.employee.resource_calendar_id, self.calendar2)
        contract.write({"resource_calendar_id": self.calendar2.id})
        self.assertNotEqual(self.employee.resource_calendar_id, self.calendar2)

    def test_contract_write(self):
        self.contract_2.write({"resource_calendar_id": self.calendar2.id})
        self.assertNotEqual(self.employee.resource_calendar_id, self.calendar2)
