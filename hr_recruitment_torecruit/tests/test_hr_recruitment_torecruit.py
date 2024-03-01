from odoo import fields

from odoo.addons.base.tests.common import BaseCommon


class TestHRJobPostionPublish(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.calendar = cls.env.ref("resource.resource_calendar_std")
        cls.job = cls.env["hr.job"].create(
            {
                "name": "Test Job",
                "no_of_recruitment": 3,
                "website_published": True,
            }
        )
        cls.employee_1 = cls.env["hr.employee"].create(
            {"name": "Test employee 1", "job_id": cls.job.id}
        )
        cls.employee_2 = cls.env["hr.employee"].create(
            {"name": "Test employee 2", "job_id": cls.job.id}
        )
        cls.employee_3 = cls.env["hr.employee"].create(
            {"name": "Test employee 3", "job_id": cls.job.id}
        )

        cls.contract_1 = cls.env["hr.contract"].create(
            {
                "name": "Test employee 1",
                "employee_id": cls.employee_1.id,
                "resource_calendar_id": cls.calendar.id,
                "date_start": fields.date.today(),
                "job_id": cls.job.id,
                "wage": 100,
            }
        )
        cls.contract_2 = cls.env["hr.contract"].create(
            {
                "name": "Test employee 2",
                "employee_id": cls.employee_2.id,
                "resource_calendar_id": cls.calendar.id,
                "date_start": fields.date.today(),
                "job_id": cls.job.id,
                "wage": 100,
            }
        )
        cls.contract_3 = cls.env["hr.contract"].create(
            {
                "name": "Test employee 3",
                "employee_id": cls.employee_3.id,
                "resource_calendar_id": cls.calendar.id,
                "date_start": fields.date.today(),
                "job_id": cls.job.id,
                "wage": 100,
            }
        )

    def test_job_postion_published(self):
        self.assertTrue(self.job.website_published)
        self.assertEqual(self.job.to_recruit, self.job.no_of_recruitment)
        self.contract_1.state = "open"
        self.contract_2.state = "open"
        self.contract_3.state = "open"
        self.job._compute_to_recruit()
        self.assertEqual(self.job.to_recruit, 0)
        self.assertFalse(self.job.website_published)
        self.contract_3.unlink()
        self.job._compute_to_recruit()
        self.assertEqual(self.job.to_recruit, 1)
        self.assertTrue(self.job.website_published)
