# Copyright 2024 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta
from itertools import product as iter_cartesian

from odoo import Command, fields
from odoo.tests.common import TransactionCase


class TestTimesheetPrefill(TransactionCase):
    """
    Tests for timesheet.prefill
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Wizard = cls.env["timesheet.prefill"]
        cls.employees = cls.env["hr.employee"].search([], limit=4)
        cls.projects = cls.env["project.project"].search([], limit=2)
        cls.today = fields.Date.today()

    def _check_action_generate_result(self, wizard):
        """
        Process the timesheet line generation and ensure the result is valid
        """
        timesheet_lines = wizard._action_generate()
        for timesheet_line, (date, employee, project) in zip(
            timesheet_lines,
            iter_cartesian(
                wizard._date_range_list(), wizard.employee_ids, wizard.project_ids
            ),
            strict=True,
        ):
            self.assertEqual(timesheet_line.date, date)
            self.assertEqual(timesheet_line.employee_id, employee)
            self.assertEqual(timesheet_line.project_id, project)
            # The unit_amount should be set with 0 as default value
            self.assertAlmostEqual(timesheet_line.unit_amount, 0)

    def test_date_range_list1(self):
        """
        Ensure the function _date_range_list generate correct date range (with correct order).
        Try with a single date.
        """
        wizard = self.Wizard.create(
            {
                "project_ids": [Command.set(self.projects.ids)],
                "employee_ids": [Command.set(self.employees.ids)],
                "date_from": self.today,
                "date_to": self.today + timedelta(days=0),
            }
        )
        expected_dates = []
        expected_date = wizard.date_from
        while expected_date <= wizard.date_to:
            expected_dates.append(expected_date)
            expected_date = expected_date + timedelta(days=1)
        generated_dates = list(wizard._date_range_list())
        self.assertListEqual(expected_dates, generated_dates)

    def test_date_range_list2(self):
        """
        Ensure the function _date_range_list generate correct date range (with correct order).
        Try with a large date range
        """
        wizard = self.Wizard.create(
            {
                "project_ids": [Command.set(self.projects.ids)],
                "employee_ids": [Command.set(self.employees.ids)],
                "date_from": self.today,
                "date_to": self.today + timedelta(days=52),
            }
        )
        expected_dates = []
        expected_date = wizard.date_from
        while expected_date <= wizard.date_to:
            expected_dates.append(expected_date)
            expected_date = expected_date + timedelta(days=1)
        generated_dates = list(wizard._date_range_list())
        self.assertListEqual(expected_dates, generated_dates)

    def test_action_generate1(self):
        """
        Ensure the _action_generate works properly:
        - Generate expected timesheet lines with correct values (small range)
        """
        wizard = self.Wizard.create(
            {
                "project_ids": [Command.set(self.projects.ids)],
                "employee_ids": [Command.set(self.employees.ids)],
                "date_from": self.today,
                "date_to": self.today + timedelta(days=1),
            }
        )
        self._check_action_generate_result(wizard)

    def test_action_generate2(self):
        """
        Ensure the _action_generate works properly:
        - Generate expected timesheet lines with correct values (large range)
        """
        wizard = self.Wizard.create(
            {
                "project_ids": [Command.set(fields.first(self.projects).ids)],
                "employee_ids": [Command.set(self.employees.ids)],
                "date_from": self.today,
                "date_to": self.today + timedelta(days=41),
            }
        )
        self._check_action_generate_result(wizard)
