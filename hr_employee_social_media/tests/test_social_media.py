# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestEmployeeSocialMedia(TransactionCase):

    def setUp(self):
        super().setUp()

        self.employee_id = self.env['hr.employee'].create({'name': 'Employee'})

        self.social_media_id = self.env['hr.social.media'].create({
            'name': 'Github',
            'social_url': 'www.github.com'
        })
        self.social_media_account = self.env['hr.social.media.account'].create(
            {
                'hr_social_media_id': self.social_media_id.id,
                'account_name': 'Account',
                'employee_id': self.employee_id.id
            }
        )

    def test_compute_name(self):
        self.assertEqual(self.social_media_account.name, 'Account (Github)')
