# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import AccessError
from odoo.tests.common import SavepointCase


class TestHrRecruitmentSecurity(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Users
        users = cls.env["res.users"].with_context(no_reset_password=True)
        # hr_officer_own_documents
        group_name = "group_hr_recruitment_officer_own_documents"
        cls.user_hr_own_documents = users.create(
            {
                "name": "hr_officer_own_documents",
                "login": "hr_officer_own_documents",
                "email": "hr_officer_own_documents@example.com",
                "groups_id": [
                    (6, 0, [cls.env.ref("hr_recruitment_security.%s" % group_name).id])
                ],
            }
        )
        # hr_user
        cls.user_hr_user = users.create(
            {
                "name": "hr_user",
                "login": "hr_user",
                "email": "hr_user@example.com",
                "groups_id": [
                    (
                        6,
                        0,
                        [cls.env.ref("hr_recruitment.group_hr_recruitment_user").id],
                    )
                ],
            }
        )
        # hr_recruitment_manager
        cls.user_hr_manager = users.create(
            {
                "name": "hr_recruitment_manager",
                "login": "hr_recruitment_manager",
                "email": "hr_recruitment_manager@example.com",
                "groups_id": [
                    (
                        6,
                        0,
                        [cls.env.ref("hr_recruitment.group_hr_recruitment_manager").id],
                    )
                ],
            }
        )
        # without_groups
        cls.user_without_groups = users.create(
            {
                "name": "without_groups",
                "login": "without_groups",
                "email": "without_groups@example.com",
                "groups_id": False,
            }
        )
        cls.job = cls.env["hr.job"].create({"name": "hr_recruitment_security"})
        cls.applicant = cls.env["hr.applicant"].create(
            {"job_id": cls.job.id, "name": cls.job.name}
        )
        cls.user_to_check = cls.user_hr_own_documents

    def _check_permission(self, record, expected):
        domain = [("id", "=", record.id)]
        obj = self.env[record._name].with_user(self.user_to_check)
        self.assertEqual(bool(obj.search(domain)), expected)

    def _check_permission_applicant(self, user, expected):
        self.applicant.write({"user_id": user.id if user else user})
        self._check_permission(self.applicant, expected)

    def _check_permission_job(self, user, responsible, expected):
        self.job.write(
            {
                "user_id": user.id if user else user,
                "hr_responsible_id": responsible.id if responsible else responsible,
            }
        )
        self._check_permission(self.job, expected)

    def test_access_applicant(self):
        self.user_to_check = self.user_hr_own_documents
        self._check_permission_applicant(False, False)
        self._check_permission_applicant(self.user_hr_own_documents, True)
        self.user_to_check = self.user_hr_user
        self._check_permission_applicant(False, True)
        self._check_permission_applicant(self.user_hr_user, True)
        self.user_to_check = self.user_hr_manager
        self._check_permission_applicant(False, True)
        self._check_permission_applicant(self.user_hr_manager, True)
        self.user_to_check = self.user_without_groups
        with self.assertRaises(AccessError):
            self._check_permission_applicant(False, False)

    def test_access_job(self):
        self.user_to_check = self.user_hr_own_documents
        self._check_permission_job(False, False, False)
        self._check_permission_job(self.user_hr_own_documents, False, False)
        self._check_permission_job(False, self.user_hr_own_documents, True)
        self.user_to_check = self.user_hr_user
        self._check_permission_job(False, False, True)
        self._check_permission_job(self.user_hr_user, False, True)
        self._check_permission_job(False, self.user_hr_user, True)
        self.user_to_check = self.user_hr_manager
        self._check_permission_job(False, False, True)
        self._check_permission_job(self.user_hr_manager, False, True)
        self._check_permission_job(False, self.user_hr_manager, True)
        self.user_to_check = self.user_without_groups
        with self.assertRaises(AccessError):
            self._check_permission_job(False, False, False)
