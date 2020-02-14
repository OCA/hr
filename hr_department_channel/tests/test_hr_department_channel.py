# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestHrDepartmentChannel(TransactionCase):

    def setUp(self):
        super(TestHrDepartmentChannel, self).setUp()
        self.employee_1 = self.create_employee('emp1')
        self.employee_2 = self.create_employee('emp2')
        self.employee_3 = self.create_employee('emp3')
        self.department_id = self.env['hr.department'].create({
            'name': 'Department',
            'manager_id': self.employee_1.id
        })

    def create_employee(self, login):
        user_id = self.env['res.users'].create({
            'name': login,
            'login': login,
            'notification_type': 'inbox'
        })
        return self.env['hr.employee'].create({
            'name': login, 'user_id': user_id.id
        })

    def test_hr_department_channel(self):
        wizard = self.env['wizard.create.department.channel'].create({
            'name': 'Channel'
        })
        wizard.with_context(active_id=self.department_id.id).generate_channel()
        self.assertEqual(self.department_id.department_channel_count, 1)
        channel = self.department_id.department_channel_ids[0]

        # The channel only has the manager
        self.assertEqual(len(channel.channel_partner_ids), 1)
        self.assertEqual(
            channel.channel_partner_ids[0].id,
            self.employee_1.user_id.partner_id.id
        )

        # Employee 2 also belongs to the department
        self.employee_2.write({'department_id': self.department_id.id})
        self.assertEqual(len(channel.channel_partner_ids), 2)

        # Manager is now employee 3 so employee 1 leaves the chat
        self.department_id.write({'manager_id': self.employee_3.id})
        self.assertEqual(len(channel.channel_partner_ids), 2)
        self.assertNotIn(
            self.employee_1.user_id.partner_id.id,
            channel.channel_partner_ids.ids
        )
