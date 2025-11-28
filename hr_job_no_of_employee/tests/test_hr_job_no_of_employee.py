# Copyright 2025 PT Solusi Aglis Indonesia. (https://solusiaglis.co.id)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestHrJobNoOfEmployee(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create test department
        cls.department = cls.env["hr.department"].create(
            {
                "name": "Test Department",
            }
        )

        # Create test job positions
        cls.job_developer = cls.env["hr.job"].create(
            {
                "name": "Software Developer",
                "department_id": cls.department.id,
                "no_of_recruitment": 5,
            }
        )

        cls.job_manager = cls.env["hr.job"].create(
            {
                "name": "Project Manager",
                "department_id": cls.department.id,
                "no_of_recruitment": 2,
            }
        )

        # Create test employees
        cls.employee_1 = cls.env["hr.employee"].create(
            {
                "name": "Employee 1",
                "job_id": cls.job_developer.id,
                "department_id": cls.department.id,
            }
        )

        cls.employee_2 = cls.env["hr.employee"].create(
            {
                "name": "Employee 2",
                "job_id": cls.job_developer.id,
                "department_id": cls.department.id,
            }
        )

        cls.employee_3 = cls.env["hr.employee"].create(
            {
                "name": "Employee 3",
                "job_id": cls.job_developer.id,
                "department_id": cls.department.id,
            }
        )

        cls.employee_4 = cls.env["hr.employee"].create(
            {
                "name": "Employee 4",
                "job_id": cls.job_manager.id,
                "department_id": cls.department.id,
            }
        )

    def test_employee_count_computation(self):
        """Test that employee_count is computed correctly"""
        # Refresh to ensure compute is triggered
        self.job_developer.invalidate_recordset()
        self.job_manager.invalidate_recordset()

        # Check employee count for developer job
        self.assertEqual(
            self.job_developer.employee_count,
            3,
            "Developer job should have 3 employees",
        )

        # Check employee count for manager job
        self.assertEqual(
            self.job_manager.employee_count, 1, "Manager job should have 1 employee"
        )

    def test_employee_count_zero(self):
        """Test employee_count is zero when no employees assigned"""
        job_empty = self.env["hr.job"].create(
            {
                "name": "Empty Job Position",
                "department_id": self.department.id,
            }
        )

        self.assertEqual(
            job_empty.employee_count, 0, "Job with no employees should have count of 0"
        )

    def test_employee_count_update_on_assignment(self):
        """Test that employee_count updates when employee is assigned"""
        # Create new job
        job_new = self.env["hr.job"].create(
            {
                "name": "New Job Position",
                "department_id": self.department.id,
            }
        )

        # Initially should be 0
        self.assertEqual(job_new.employee_count, 0)

        # Assign employee to new job
        new_employee = self.env["hr.employee"].create(
            {
                "name": "New Employee",
                "job_id": job_new.id,
                "department_id": self.department.id,
            }
        )

        # Refresh and check count
        job_new.invalidate_recordset()
        self.assertEqual(
            job_new.employee_count, 1, "Job should have 1 employee after assignment"
        )

        # Change employee job
        new_employee.job_id = self.job_developer.id

        # Refresh and check both jobs
        job_new.invalidate_recordset()
        self.job_developer.invalidate_recordset()

        self.assertEqual(
            job_new.employee_count,
            0,
            "Original job should have 0 employees after reassignment",
        )
        self.assertEqual(
            self.job_developer.employee_count,
            4,
            "Developer job should have 4 employees after reassignment",
        )

    def test_action_open_employees(self):
        """Test action_open_employees returns correct action"""
        action = self.job_developer.action_open_employees()

        # Check action structure
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertIn(action["res_model"], ["hr.employee", "hr.employee.public"])
        self.assertEqual(action["view_mode"], "list,kanban,form")

        # Check context
        self.assertEqual(action["context"]["default_job_id"], self.job_developer.id)
        self.assertEqual(
            action["context"]["search_default_job_id"], self.job_developer.id
        )

    def test_multiple_jobs_employee_count(self):
        """Test employee_count for multiple jobs at once"""
        jobs = self.job_developer | self.job_manager

        # Force recompute
        jobs.invalidate_recordset()

        counts = {job.id: job.employee_count for job in jobs}

        self.assertEqual(counts[self.job_developer.id], 3)
        self.assertEqual(counts[self.job_manager.id], 1)

    def test_employee_count_with_archived_employees(self):
        """Test that archived employees are not counted"""
        # Archive one employee
        self.employee_1.active = False

        # Refresh and check count
        self.job_developer.invalidate_recordset()

        self.assertEqual(
            self.job_developer.employee_count,
            2,
            "Archived employees should not be counted",
        )
