# Copyright 2026 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import Command, models
from odoo.tests.common import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class HrEmployeeMedicalExaminationCommon(BaseCommon):
    _test_user_groups = ("base.group_user", "hr.group_hr_manager")

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.company_two = cls.env["res.company"].create({"name": "TA43358 Company Two"})
        company_ids = Command.set([cls.company.id, cls.company_two.id])
        cls._test_user.company_ids = [company_ids]
        cls.owner_one = new_test_user(
            cls.env,
            login="ta43358_owner_one",
            groups="base.group_user",
            company_id=cls.company.id,
            company_ids=[company_ids],
        )
        cls.owner_two = new_test_user(
            cls.env,
            login="ta43358_owner_two",
            groups="base.group_user",
            company_id=cls.company.id,
            company_ids=[company_ids],
        )
        cls.hr_officer = new_test_user(
            cls.env,
            login="ta43358_hr_officer",
            groups="base.group_user,hr.group_hr_user",
            company_id=cls.company.id,
            company_ids=[company_ids],
        )

        cls.department = cls.env["hr.department"].create({"name": "TA43358 Department"})
        cls.subdepartment = cls.env["hr.department"].create(
            {
                "name": "TA43358 Subdepartment",
                "parent_id": cls.department.id,
            }
        )
        cls.other_department = cls.env["hr.department"].create(
            {"name": "TA43358 Other Department"}
        )
        cls.job = cls.env["hr.job"].create({"name": "TA43358 Job"})
        cls.other_job = cls.env["hr.job"].create({"name": "TA43358 Other Job"})

        cls.employee_one = cls._create_employee(
            "TA43358 Employee One",
            cls.owner_one,
            cls.company,
            cls.department,
            cls.job,
        )
        cls.employee_two = cls._create_employee(
            "TA43358 Employee Two",
            cls.owner_two,
            cls.company_two,
            cls.subdepartment,
            cls.job,
        )
        cls.employee_officer = cls._create_employee(
            "TA43358 Officer Employee",
            cls.hr_officer,
            cls.company,
            cls.subdepartment,
            cls.other_job,
        )
        cls.employee_outside = cls._create_employee(
            "TA43358 Outside Employee",
            None,
            cls.company,
            cls.other_department,
            cls.job,
        )

        examinations = cls.env["hr.employee.medical.examination"]
        cls.examination_one = examinations.create(
            {"name": "TA43358 Examination One", "employee_id": cls.employee_one.id}
        )
        cls.examination_two = examinations.create(
            {"name": "TA43358 Examination Two", "employee_id": cls.employee_two.id}
        )
        cls.examination_officer = examinations.create(
            {
                "name": "TA43358 Officer Examination",
                "employee_id": cls.employee_officer.id,
            }
        )

    @classmethod
    def _create_employee(
        cls,
        name: str,
        user: models.Model | None,
        company: models.Model,
        department: models.Model,
        job: models.Model,
    ) -> models.Model:
        return cls.env["hr.employee"].create(
            {
                "name": name,
                "user_id": user.id if user else False,
                "company_id": company.id,
                "department_id": department.id,
                "job_id": job.id,
            }
        )
