# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import AccessError

from .common import HrEmployeeMedicalExaminationCommon


class TestHrEmployeeMedicalExamination(HrEmployeeMedicalExaminationCommon):
    def test_01_campaign_includes_subdepartments_and_only_selected_employees(
        self,
    ) -> None:
        wizard = (
            self.env["wizard.generate.medical.examination"]
            .with_context(allowed_company_ids=[self.company.id, self.company_two.id])
            .create(
                {
                    "name": "TA43358 Campaign",
                    "year": "2026",
                    "department_id": self.department.id,
                    "job_id": self.job.id,
                }
            )
        )

        wizard.populate()

        self.assertEqual(
            set(wizard.employee_ids.ids),
            {self.employee_one.id, self.employee_two.id},
        )
        self.assertNotIn(self.employee_outside.id, wizard.employee_ids.ids)
        wizard.write({"employee_ids": [Command.unlink(self.employee_two.id)]})
        action = wizard.create_medical_examinations()
        examinations = self.env["hr.employee.medical.examination"].search(
            action["domain"]
        )

        self.assertEqual(len(examinations), 1)
        self.assertEqual(examinations.employee_id, self.employee_one)
        self.assertEqual(examinations.year, "2026")
        self.assertEqual(action["res_model"], "hr.employee.medical.examination")

    def test_02_examination_lifecycle_chatter_and_activity(self) -> None:
        examination = self.env["hr.employee.medical.examination"].create(
            {
                "name": "TA43358 Lifecycle Examination",
                "employee_id": self.employee_officer.id,
                "note": "Initial medical note",
            }
        )
        examination.write(
            {
                "date": "2024-05-05",
                "result": "passed",
                "note": "Cleared for work",
            }
        )
        examination._onchange_date()

        self.assertEqual(examination.year, "2024")
        self.assertEqual(examination.result, "passed")
        self.assertEqual(examination.note, "Cleared for work")
        self.assertEqual(self.employee_officer.medical_examination_count, 2)
        examination.to_done()
        self.assertEqual(examination.state, "done")
        examination.to_cancelled()
        self.assertEqual(examination.state, "cancelled")
        examination.to_rejected()
        self.assertEqual(examination.state, "rejected")
        examination.back_to_pending()
        self.assertEqual(examination.state, "pending")

        message = examination.message_post(body="Medical examination reviewed")
        self.assertIn(message, examination.message_ids)

        activity = examination.activity_schedule(
            act_type_xmlid="mail.mail_activity_data_todo",
            date_deadline="2024-05-06",
            summary="Review medical examination",
            user_id=self._test_user.id,
        )
        self.assertIn(activity, examination.activity_ids)

    def test_03_users_and_officers_only_read_their_own_examinations(self) -> None:
        examinations = self.env["hr.employee.medical.examination"]
        company_context = {
            "allowed_company_ids": [self.company.id, self.company_two.id]
        }
        owner_one_examinations = (
            examinations.with_user(self.owner_one)
            .with_context(**company_context)
            .search([])
        )
        owner_two_examinations = (
            examinations.with_user(self.owner_two)
            .with_context(**company_context)
            .search([])
        )
        officer_examinations = (
            examinations.with_user(self.hr_officer)
            .with_context(**company_context)
            .search([])
        )

        self.assertEqual(owner_one_examinations.ids, [self.examination_one.id])
        self.assertEqual(owner_two_examinations.ids, [self.examination_two.id])
        self.assertEqual(officer_examinations.ids, [self.examination_officer.id])

        for user, examination in (
            (self.owner_one, self.examination_two),
            (self.owner_two, self.examination_one),
            (self.hr_officer, self.examination_one),
        ):
            with self.subTest(user=user.login), self.assertRaises(AccessError):
                examinations.with_user(user).browse(examination.id).read(["name"])

        for user, examination in (
            (self.owner_one, self.examination_one),
            (self.hr_officer, self.examination_officer),
        ):
            restricted_examinations = examinations.with_user(user).with_context(
                **company_context
            )
            with (
                self.subTest(user=user.login, operation="create"),
                self.assertRaises(AccessError),
            ):
                restricted_examinations.create(
                    {
                        "name": "TA43358 Forbidden Examination",
                        "employee_id": examination.employee_id.id,
                    }
                )
            with (
                self.subTest(user=user.login, operation="write"),
                self.assertRaises(AccessError),
            ):
                restricted_examinations.browse(examination.id).write(
                    {"note": "Forbidden update"}
                )
            with (
                self.subTest(user=user.login, operation="unlink"),
                self.assertRaises(AccessError),
            ):
                restricted_examinations.browse(examination.id).unlink()

        manager_examinations = examinations.with_user(self._test_user).with_context(
            allowed_company_ids=[self.company.id, self.company_two.id]
        )
        self.assertEqual(
            set(manager_examinations.search([]).ids),
            {
                self.examination_one.id,
                self.examination_two.id,
                self.examination_officer.id,
            },
        )
        created = manager_examinations.create(
            {
                "name": "TA43358 Manager Examination Two",
                "employee_id": self.employee_two.id,
            }
        )
        created_one = manager_examinations.create(
            {
                "name": "TA43358 Manager Examination One",
                "employee_id": self.employee_one.id,
            }
        )
        manager_examinations.browse(self.examination_one.id).write(
            {"note": "Manager update"}
        )
        manager_examinations.browse(self.examination_two.id).write(
            {"note": "Manager update"}
        )
        manager_examinations.browse(self.examination_one.id).unlink()
        manager_examinations.browse(self.examination_two.id).unlink()

        self.assertEqual(created.employee_id, self.employee_two)
        self.assertEqual(created_one.employee_id, self.employee_one)
        self.assertFalse(manager_examinations.browse(self.examination_one.id).exists())
        self.assertFalse(manager_examinations.browse(self.examination_two.id).exists())

    def test_04_campaign_respects_active_companies(self) -> None:
        wizard_model = self.env["wizard.generate.medical.examination"].with_user(
            self.hr_officer
        )
        one_company_wizard = wizard_model.with_context(
            allowed_company_ids=[self.company.id]
        ).create(
            {
                "name": "TA43358 One Company Campaign",
                "department_id": self.department.id,
                "job_id": self.job.id,
            }
        )
        one_company_wizard.populate()

        both_companies_wizard = wizard_model.with_context(
            allowed_company_ids=[self.company.id, self.company_two.id]
        ).create(
            {
                "name": "TA43358 Two Company Campaign",
                "department_id": self.department.id,
                "job_id": self.job.id,
            }
        )
        both_companies_wizard.populate()

        self.assertEqual(one_company_wizard.employee_ids.ids, [self.employee_one.id])
        self.assertEqual(
            set(both_companies_wizard.employee_ids.ids),
            {self.employee_one.id, self.employee_two.id},
        )
