# Copyright 2014 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestHrJobCategories(common.TransactionCase):
    def setUp(self):
        super(TestHrJobCategories, self).setUp()
        self.employee_model = self.env["hr.employee"]
        self.employee_categ_model = self.env["hr.employee.category"]
        self.user_model = self.env["res.users"]
        self.job_model = self.env["hr.job"]
        self.contract_model = self.env["hr.contract"]

        # Create a employee
        self.employee_id_1 = self.employee_model.create({"name": "Employee 1"})
        self.employee_id_2 = self.employee_model.create({"name": "Employee 2"})

        # Create two employee categories
        self.categ_id = self.employee_categ_model.create({"name": "Category 1"})
        self.categ_2_id = self.employee_categ_model.create({"name": "Category 2"})

        # Create two jobs
        self.job_id = self.job_model.create(
            {"name": "Job 1", "category_ids": [(6, 0, [self.categ_id.id])]}
        )

        self.job_2_id = self.job_model.create(
            {"name": "Job 2", "category_ids": [(6, 0, [self.categ_2_id.id])]}
        )

        # Create one contract
        self.contract_id = self.contract_model.create(
            {"name": "Contract 1", "employee_id": self.employee_id_1.id, "wage": 50000}
        )

    def test_write_computes_with_normal_args(self):
        """
        Test that write method on hr_contract computes without error
        when the required data is given in parameter

        Check if the job categories are written to the employee.
        """
        # Check if job categories are written to the employee
        self.contract_id.write({"job_id": self.job_id.id})
        self.contract_id.refresh()
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
        self.contract_id.flush()
        self.assertTrue(
            all(
                x in self.employee_id_1.category_ids.ids
                for x in self.job_2_id.category_ids.ids
            )
        )
        self.contract_id.write({"employee_id": self.employee_id_2.id})
        self.contract_id.write({"job_id": self.job_2_id.id})
        # We need to force the job, as it is modified by a compute
        self.employee_id_1.refresh()
        self.employee_id_2.refresh()
        self.assertFalse(self.employee_id_1.category_ids)
        self.job_2_id.refresh()
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
        categ_3_id = self.employee_categ_model.create({"name": "Category 3"})
        self.employee_id_1.write({"category_ids": categ_3_id})
        # We have added manually a tag
        self.assertEquals(len(self.employee_id_1.category_ids.ids),1)
        self.assertEquals(self.employee_id_1.category_ids.ids[0], categ_3_id.id)
        # We are now adding contract with 1 job category
        # The employee should now have two tags
        self.contract_id.write({"job_id": self.job_id.id})
        self.contract_id.refresh()
        self.assertEquals(len(self.employee_id_1.category_ids.ids),2)
        self.assertEquals(self.employee_id_1.category_ids.ids[0], categ_3_id.id)
        self.assertEquals(self.employee_id_1.category_ids.ids[1], self.job_2_id.category_ids.ids[0])
