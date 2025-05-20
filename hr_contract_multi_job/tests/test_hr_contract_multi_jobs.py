# Copyright 2014 Savoir-faire Linux. All Rights Reserved.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestContractMultiJob(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee_model = cls.env["hr.employee"]
        cls.user_model = cls.env["res.users"]
        cls.contract_model = cls.env["hr.contract"]
        cls.job_model = cls.env["hr.job"]

        # Create an employee
        cls.employee = cls.employee_model.create({"name": "Employee 1"})

        # Create 2 jobs
        cls.job_1 = cls.job_model.create({"name": "Job 1"})

        cls.job_2 = cls.job_model.create({"name": "Job 2"})

        # Create a contract
        cls.contract = cls.contract_model.create(
            {"employee_id": cls.employee.id, "name": "Contract 1", "wage": 50000}
        )

    def test_no_main_jobs(self):
        """
        Validate the _check_one_main_job method
        when contract has no assigned job
        and check job_1 is False.
        """
        self.contract.contract_job_ids = [Command.clear()]
        self.assertFalse(self.contract.job_id is False)

    def test_one_main_jobs(self):
        """
        Validate the _check_one_main_job method
        when contract has one assigned job
        and check is the job_1 is set.
        """
        self.contract.write(
            {
                "contract_job_ids": [
                    Command.create({"job_id": self.job_1.id, "is_main_job": True})
                ]
            }
        )
        self.assertEqual(self.contract.job_id.id, self.job_1.id)

    def test_two_contract_jobs_one_main_job(self):
        """
        Validate the _check_one_main_job method
        when contract has two assigned jobs
        and check is the job_1 is set as main job.
        """
        self.contract.write(
            {
                "contract_job_ids": [
                    Command.create({"job_id": self.job_1.id, "is_main_job": True}),
                    Command.create({"job_id": self.job_2.id, "is_main_job": False}),
                ]
            }
        )
        self.assertEqual(self.contract.job_id.id, self.job_1.id)

    def test_two_contract_jobs_two_main_job(self):
        """
        Validate the _check_one_main_job method
        when contract has two assigned jobs
        and raise error since both are set as main jobs.
        """
        with self.assertRaises(UserError):
            self.contract.write(
                {
                    "contract_job_ids": [
                        Command.create({"job_id": self.job_1.id, "is_main_job": True}),
                        Command.create({"job_id": self.job_2.id, "is_main_job": True}),
                    ]
                }
            )
