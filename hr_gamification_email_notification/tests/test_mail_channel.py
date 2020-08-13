# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime
from dateutil.relativedelta import relativedelta

from odoo.tests import common


class TestMailChannel(common.TransactionCase):

    def setUp(self):
        super(TestMailChannel, self).setUp()
        employees_group = self.env.ref('base.group_user')
        self.user_ids = employees_group.users
        self.test_employee = self.browse_ref('hr.employee_al')

        self.robot = self.env['res.users'].with_context(
            no_reset_password=True).create({
                'name': 'R2D2',
                'login': 'r2d2@odoo.com',
                'email': 'r2d2@odoo.com',
                'groups_id': [(6, 0, [employees_group.id])]
            })
        self.badge_good_job = self.env.ref('gamification.badge_good_job')
        self.channel_general = self.env['mail.channel'].search(
            [('name', '=', 'general')], limit=1)

    def test_send_badge_awards_emails(self):
        self.test_employee.user_id = self.robot.id
        wiz = self.env['gamification.badge.user.wizard'].create({
            'badge_id': self.badge_good_job.id,
            'employee_id': self.test_employee.id
        })
        wiz.create_date = datetime.datetime.now() - relativedelta(days=1)
        wiz.action_grant_badge()
        self.assertTrue(
            self.channel_general._send_badge_awards_emails(),
            "Could not sent emails")
