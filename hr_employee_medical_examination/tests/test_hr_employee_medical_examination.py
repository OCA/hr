# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestHrEmployeeMedicalExamination(TransactionCase):
    def setUp(self):
        super().setUp()

        self.department = self.env["hr.department"].create({"name": "Department"})

        self.job = self.env["hr.job"].create({"name": "Job"})

        self.employee1 = self.env["hr.employee"].create(
            {
                "name": "Employee 1",
                "job_id": self.job.id,
                "department_id": self.department.id,
            }
        )

        self.examination = self.env["hr.employee.medical.examination"].create(
            {"name": "Dummy Exam to test domain", "employee_id": self.employee1.id}
        )

        self.wizard = self.env["wizard.generate.medical.examination"].create(
            {"name": "Examination 2019"}
        )

    def test_hr_employee_medical_examination(self):
        self.assertFalse(self.wizard.employee_ids)
        self.wizard.write({"job_id": self.job.id, "department_id": self.department.id})
        self.wizard.populate()
        self.assertEqual(len(self.wizard.employee_ids), 1)
        result = self.wizard.create_medical_examinations()

        examination = self.env["hr.employee.medical.examination"].search(
            result["domain"]
        )
        self.assertTrue(examination)
        self.assertEqual(1, len(examination))
        self.assertEqual(examination.name, "Examination 2019 on Employee 1")
        self.assertEqual(self.employee1.medical_examination_count, 2)
        self.assertTrue(self.employee1.can_see_examinations_button)
        examination.write({"date": "2018-05-05"})
        examination._onchange_date()
        self.assertEqual(examination.year, "2018")
        examination.to_done()
        self.assertEqual(examination.state, "done")
        examination.to_cancelled()
        self.assertEqual(examination.state, "cancelled")
        examination.to_rejected()
        self.assertEqual(examination.state, "rejected")
        examination.back_to_pending()
        self.assertEqual(examination.state, "pending")
