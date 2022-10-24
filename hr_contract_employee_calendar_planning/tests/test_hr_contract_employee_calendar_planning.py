from datetime import datetime

from odoo.addons.hr_contract.tests.common import TestContractCommon

from ..hooks import post_init_hook


class TestHrContractEmployeeCalendarPlanning(TestContractCommon):
    def setUp(self):
        super().setUp()
        calendar_ids = [
            (
                0,
                0,
                {
                    "date_start": False,
                    "date_end": datetime.strptime("2020-11-30", "%Y-%m-%d").date(),
                    "calendar_id": self.env["resource.calendar"].browse([2]).id,
                },
            ),
            (
                0,
                0,
                {
                    "date_start": datetime.strptime("2020-12-01", "%Y-%m-%d").date(),
                    "date_end": False,
                    "calendar_id": self.env["resource.calendar"].browse([1]).id,
                },
            ),
        ]
        self.employee.calendar_ids = calendar_ids

    def test_calendar_migration_from_contracts(self):
        self.contract1 = self.env["hr.contract"].create(
            {
                "name": "contract1",
                "employee_id": self.employee.id,
                "wage": 1,
                "state": "close",
                "kanban_state": "normal",
                "resource_calendar_id": self.env["resource.calendar"].browse([1]).id,
                "date_start": datetime.strptime("2018-11-30", "%Y-%m-%d").date(),
                "date_end": datetime.strptime("2019-11-30", "%Y-%m-%d").date(),
            }
        )
        self.contract2 = self.env["hr.contract"].create(
            {
                "name": "contract2",
                "employee_id": self.employee.id,
                "wage": 1,
                "state": "open",
                "kanban_state": "normal",
                "resource_calendar_id": self.env["resource.calendar"].browse([2]).id,
                "date_start": datetime.strptime("2019-12-01", "%Y-%m-%d").date(),
                "date_end": datetime.strptime("2020-11-30", "%Y-%m-%d").date(),
            }
        )
        original_cal_ids = self.employee.calendar_ids.ids
        start_dt = datetime(2019, 1, 1, 0, 0, 0)
        end_dt = datetime(2019, 1, 2, 0, 0, 0)
        self.assertEqual(
            7.0,
            self.employee.resource_calendar_id.get_work_hours_count(
                start_dt=start_dt,
                end_dt=end_dt,
            ),
        )
        # calendar migration from contracts
        post_init_hook(self.env.cr, self.env.registry, self.employee)
        self.assertEqual(
            8.0,
            self.employee.resource_calendar_id.get_work_hours_count(
                start_dt=start_dt,
                end_dt=end_dt,
            ),
        )
        self.assertTrue(
            all(ids in self.employee.calendar_ids.ids for ids in original_cal_ids)
        )
