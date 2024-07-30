# Copyright 2014 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestHrJobCategories(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee_model = cls.env["hr.employee"]
        cls.employee_categ_model = cls.env["hr.employee.category"]
        cls.user_model = cls.env["res.users"]
        cls.job_model = cls.env["hr.job"]
        cls.contract_model = cls.env["hr.contract"]

        # Create a employee
        cls.employee_id_1 = cls.employee_model.create({"name": "Employee 1"})
        cls.employee_id_2 = cls.employee_model.create({"name": "Employee 2"})

        # Create two employee categories for job positions
        cls.categ_id = cls.employee_categ_model.create({"name": "Category 1"})
        cls.categ_2_id = cls.employee_categ_model.create({"name": "Category 2"})

        # Create an employee category to be used out of job positions
        cls.categ_3_id = cls.employee_categ_model.create({"name": "Category 3"})

        # Create two jobs
        cls.job_id = cls.job_model.create(
            {"name": "Job 1", "category_ids": [(6, 0, [cls.categ_id.id])]}
        )

        cls.job_2_id = cls.job_model.create(
            {"name": "Job 2", "category_ids": [(6, 0, [cls.categ_2_id.id])]}
        )

        # Create one contract
        cls.contract_id = cls.contract_model.create(
            {"name": "Contract 1", "employee_id": cls.employee_id_1.id, "wage": 50000}
        )

    def test_write_computes_with_normal_args(self):
        """
        Test that write method on hr_contract computes without error
        when the required data is given in parameter

        Check if the job categories are written to the employee.
        """
        # Check if job categories are written to the employee
        self.contract_id.write({"job_id": self.job_id.id})
        self.assertTrue(self.employee_id_1.category_ids)
        self.assertTrue(
            all(
                x in self.employee_id_1.category_ids.ids
                for x in self.job_id.category_ids.ids
            )
        )

        self.contract_id.write({"job_id": False})
        self.assertFalse(self.employee_id_1.category_ids)

        # Check if job2 categories are written to the employee
        self.contract_id.write({"job_id": self.job_2_id.id})
        self.assertTrue(
            all(
                x in self.employee_id_1.category_ids.ids
                for x in self.job_2_id.category_ids.ids
            )
        )
        self.contract_id.write({"employee_id": self.employee_id_2.id})
        self.contract_id.write({"job_id": self.job_2_id.id})
        self.assertFalse(self.employee_id_1.category_ids)
        self.assertTrue(
            all(
                x in self.employee_id_2.category_ids.ids
                for x in self.job_2_id.category_ids.ids
            )
        )

        self.contract_id.unlink()
        self.assertFalse(self.employee_id_2.category_ids)

    def test_add_new_tags_with_already_present_tags(self):
        """
        When a tag is manually added, adding new tags from a contract shouldn't remove
        them
        """
        self.employee_id_1.write({"category_ids": self.categ_3_id})
        # We have added manually a tag
        self.assertEqual(len(self.employee_id_1.category_ids.ids), 1)
        self.assertEqual(self.employee_id_1.category_ids.ids[0], self.categ_3_id.id)
        # We are now adding contract with 1 job category
        # The employee should now have two tags
        self.contract_id.write({"job_id": self.job_id.id})
        self.assertEqual(len(self.employee_id_1.category_ids.ids), 2)
        self.assertIn(self.categ_3_id.id, self.employee_id_1.category_ids.ids)
        self.assertIn(
            self.job_id.category_ids.ids[0], self.employee_id_1.category_ids.ids
        )

    def test_remove_tags_from_previous_job(self):
        """Changing the job position removes previous tags and add the new ones"""
        self.employee_id_1.write({"category_ids": self.categ_3_id})
        self.contract_id.write({"job_id": self.job_id.id})

        # We have two tags (from job and the manual added one)
        self.assertEqual(len(self.employee_id_1.category_ids.ids), 2)

        # We change the contract of the employe
        # We should now have the tag
        self.contract_id.write({"job_id": self.job_2_id.id})

        self.assertEqual(len(self.employee_id_1.category_ids.ids), 2)
        self.assertIn(self.categ_3_id.id, self.employee_id_1.category_ids.ids)
        self.assertNotIn(
            self.job_id.category_ids.ids[0], self.employee_id_1.category_ids.ids
        )
        self.assertIn(
            self.job_2_id.category_ids.ids[0], self.employee_id_1.category_ids.ids
        )

    def test_unlink_contract(self):
        """When we unlink a contract, it should remove only the tags related to it"""
        self.employee_id_1.write({"category_ids": self.categ_3_id})
        self.contract_id.write({"job_id": self.job_id.id})

        # We have two tags (from job and the manual added one)
        self.assertEqual(len(self.employee_id_1.category_ids.ids), 2)

        self.contract_id.unlink()
        self.assertEqual(len(self.employee_id_1.category_ids.ids), 1)
        self.assertIn(self.categ_3_id.id, self.employee_id_1.category_ids.ids)
        self.assertNotIn(
            self.job_id.category_ids.ids[0], self.employee_id_1.category_ids.ids
        )
