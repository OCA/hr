# Copyright 2021 Tecnativa - João Marques
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase


class TestHrApplicationSecurity(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.new_application_mt = cls.env.ref(
            "hr_recruitment_notification.mt_hr_applicant_new"
        )
        users = cls.env["res.users"].with_context(no_reset_password=True)
        cls.user = users.create(
            {
                "name": "user_1",
                "login": "user_1",
                "email": "user_1@example.com",
                "groups_id": [
                    (4, cls.env.ref("hr.group_hr_manager").id),
                    (4, cls.env.ref("hr_recruitment.group_hr_recruitment_manager").id),
                ],
            }
        )
        cls.job = cls.env["hr.job"].create({"name": "Test Job for Notification"})
        # Make test user follow Test HR Job
        cls.env["mail.followers"].create(
            {
                "res_model": "hr.job",
                "res_id": cls.job.id,
                "partner_id": cls.user.partner_id.id,
                "subtype_ids": [(4, cls.new_application_mt.id)],
            }
        )

    def test_hr_application_notification(self):
        application = self.env["hr.applicant"].create(
            {"name": "Test Job Application for Notification", "job_id": self.job.id}
        )
        new_application_message = application.message_ids.filtered(
            lambda m: m.subtype_id == self.new_application_mt.parent_id
        )
        self.assertTrue(
            self.user.partner_id in new_application_message.notified_partner_ids
        )
