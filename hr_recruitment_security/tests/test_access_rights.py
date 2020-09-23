# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from odoo.exceptions import AccessError
from odoo.tests.common import SavepointCase

_logger = logging.getLogger(__name__)


class TestHrRecruitmentSecurity(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestHrRecruitmentSecurity, cls).setUpClass()
        # Users
        users = cls.env["res.users"].with_context(no_reset_password=True)
        # hr_officer_own_documents
        group_name = "group_hr_recruitment_officer_own_documents"
        cls.user_hr_officer_own_documents = users.create(
            {
                "name": "hr_officer_own_documents",
                "login": "hr_officer_own_documents",
                "email": "hr_officer_own_documents@example.com",
                "groups_id": [
                    (6, 0, [cls.env.ref(
                        "hr_recruitment_security.%s" % group_name
                        ).id])
                ],
            }
        )
        # hr_user
        cls.user_hr_ruser = users.create(
            {
                "name": "hr_user",
                "login": "hr_user",
                "email": "hr_user@example.com",
                "groups_id": [
                    (6, 0, [cls.env.ref("hr_recruitment.group_hr_recruitment_user").id])
                ],
            }
        )
        # hr_recruitment_manager
        cls.user_hr_recruitment_manager = users.create(
            {
                "name": "hr_recruitment_manager",
                "login": "hr_recruitment_manager",
                "email": "hr_recruitment_manager@example.com",
                "groups_id": [
                    (6, 0, [
                        cls.env.ref("hr_recruitment.group_hr_recruitment_manager").id
                    ])
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
        # hr_job
        cls.env["hr.job"].create((
            {
                "name": "hr_recruitment_security"
            },
            {
                "name": "hr_recruitment_security",
                "hr_responsible_id": cls.user_hr_ruser.id,
            },
            {
                "name": "hr_recruitment_security",
                "hr_responsible_id": cls.user_hr_recruitment_manager.id,
            },
            {
                "name": "hr_recruitment_security",
                "hr_responsible_id": cls.user_hr_officer_own_documents.id
            }
        ))
        # hr_applicant
        cls.env["hr.applicant"].create((
            {
                "job_id": cls.env["hr.job"].search([
                    ('name', '=', 'hr_recruitment_security'),
                    ('hr_responsible_id', '=', False)
                ])[0].id,
                "name": "hr_recruitment_security"
            },
            {
                "job_id": cls.env["hr.job"].search([
                    ('name', '=', 'hr_recruitment_security'),
                    ('hr_responsible_id', '=', False)
                ])[0].id,
                "name": "hr_recruitment_security",
                "user_id": cls.user_hr_ruser.id
            },
            {
                "job_id": cls.env["hr.job"].search([
                    ('name', '=', 'hr_recruitment_security'),
                    ('hr_responsible_id', '=', False)
                ])[0].id,
                "name": "hr_recruitment_security",
                "user_id": cls.user_hr_recruitment_manager.id
            },
            {
                "job_id": cls.env["hr.job"].search([
                    ('name', '=', 'hr_recruitment_security'),
                    ('hr_responsible_id', '=', False)
                ])[0].id,
                "name": "hr_recruitment_security",
                "user_id": cls.user_hr_officer_own_documents.id
            }
        ))

    def test_access_user_user_hr_officer_own_documents(self):
        self.assertEqual(
            len(
                self.env["hr.job"]
                .sudo(self.user_hr_officer_own_documents)
                .search([]).ids
            ),
            1
        )
        self.assertEqual(
            len(
                self.env["hr.applicant"]
                .sudo(self.user_hr_officer_own_documents)
                .search([]).ids
            ),
            1
        )

    def test_access_user_hr_user(self):
        self.assertEqual(
            len(
                self.env["hr.job"]
                .sudo(self.user_hr_ruser)
                .search([
                    ('name', '=', 'hr_recruitment_security')
                ]).ids
            ),
            4
        )
        self.assertEqual(
            len(
                self.env["hr.applicant"]
                .sudo(self.user_hr_ruser)
                .search([
                    ('name', '=', 'hr_recruitment_security')
                ]).ids
            ),
            4
        )

    def test_access_user_hr_recruitment_manager(self):
        self.assertEqual(
            len(
                self.env["hr.job"]
                .sudo(self.user_hr_recruitment_manager)
                .search([
                    ('name', '=', 'hr_recruitment_security')
                ]).ids
            ),
            4
        )
        self.assertEqual(
            len(
                self.env["hr.applicant"]
                .sudo(self.user_hr_recruitment_manager)
                .search([
                    ('name', '=', 'hr_recruitment_security')
                ]).ids
            ),
            4
        )

    def test_access_user_without_groups(self):
        with self.assertRaises(AccessError):
            self.env["hr.job"].sudo(self.user_without_groups).read()

        with self.assertRaises(AccessError):
            self.env["hr.applicant"].sudo(self.user_without_groups).read()
