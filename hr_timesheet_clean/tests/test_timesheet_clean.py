# Copyright 2024 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta
from itertools import product as iter_cartesian

from odoo import fields
from odoo.tests.common import TransactionCase


class TestTimesheetClean(TransactionCase):
    """
    Tests for timesheet.clean
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Wizard = cls.env["timesheet.clean"]
        cls.TimesheetLine = cls.env["account.analytic.line"]
        cls.employees = cls.env["hr.employee"].search([], limit=4)
        cls.projects = cls.env["project.project"].search([], limit=2)
        cls.today = fields.Date.today()

    def _generate_timesheet_lines(self, date):
        return self.TimesheetLine.create(
            [
                {"employee_id": employee.id, "project_id": project.id, "date": date}
                for employee, project in iter_cartesian(self.employees, self.projects)
            ]
        )

    def _check_action_clean_result(self, wizard):
        """
        Process the timesheet line cleaning and ensure the result is valid
        """
        domain = [
            ("date", "<=", wizard.date_to),
            ("date", ">=", wizard.date_from),
            ("unit_amount", "=", 0),
            ("project_id", "!=", False),
        ]
        timesheet_lines_to_delete = self.TimesheetLine.search(domain)
        timesheet_lines_to_keep = (
            self.TimesheetLine.search([]) - timesheet_lines_to_delete
        )
        wizard._action_clean()
        self.assertFalse(timesheet_lines_to_delete.exists())
        self.assertEqual(
            set(timesheet_lines_to_keep.ids), set(timesheet_lines_to_keep.exists().ids)
        )

    def test_action_clean1(self):
        """
        Ensure the _action_clean works properly:
        - Clean a large range of timesheet lines
        """
        self._generate_timesheet_lines(self.today)
        # Also generate some random analytic line who are not timesheet
        no_timesheets = self.TimesheetLine.create(
            [
                {
                    "employee_id": employee.id,
                    "project_id": False,
                    "account_id": project.analytic_account_id.id,
                    "date": self.today,
                    "name": project.name,
                }
                for employee, project in iter_cartesian(self.employees, self.projects)
            ]
        )
        self.assertTrue(all(not tl.project_id for tl in no_timesheets))
        save_no_timesheet_ids = no_timesheets.ids
        wizard = self.Wizard.create(
            {
                "date_from": self.today,
                "date_to": self.today + timedelta(days=1),
            }
        )
        self._check_action_clean_result(wizard)
        self.assertEqual(set(save_no_timesheet_ids), set(no_timesheets.exists().ids))

    def test_action_clean2(self):
        """
        Ensure the _action_clean works properly:
        - Trigger the clean when there is nothing to clean
        """
        wizard = self.Wizard.create(
            {
                "date_from": self.today,
                "date_to": self.today + timedelta(days=41),
            }
        )
        self._check_action_clean_result(wizard)
