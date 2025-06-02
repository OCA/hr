# Copyright 2025 Fundación Esment - Estefanía Bauzá Illán
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon

class TestHrAppraisalEmployee(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Employee = cls.env['hr.employee']
        cls.User = cls.env['res.users']
        cls.Template = cls.env['hr.appraisal.employee.template']
        cls.Appraisal = cls.env['hr.appraisal.employee']

        cls.user_manager = cls.User.create({
            'name': 'Manager User',
            'login': 'manager@example.com',
            'email': 'manager@example.com',
        })

        cls.employee_user = cls.User.create({
            'name': 'Employee User',
            'login': 'employee@example.com',
            'email': 'employee@example.com',
        })

        cls.department_1 = cls.env['hr.department'].create({'name': 'Department 1'})

        cls.manager = cls.Employee.create({
            'name': 'Manager',
            'user_id': cls.user_manager.id,
            'work_email': 'manager@example.com',
            'department_id': cls.department_1.id,
        })

        cls.employee = cls.Employee.create({
            'name': 'Employee',
            'user_id': cls.employee_user.id,
            'parent_id': cls.manager.id,
            'work_email': 'employee@example.com',
            'department_id': cls.department_1.id,
        })
        cls.template = cls.Template.create({
            'description': 'Default Template',
            'is_default': True,
            'appraisal_employee_feedback_template': "<p>Feedback</p>",
            'appraisal_manager_feedback_template': "<p>Manager Feedback</p>",
        })

        cls.appraisal = cls.Appraisal.create({
            'employee_id': cls.employee.id,
            'manager_ids': [(6, 0, [cls.manager.id])],
            'date_close': '2025-12-31',
            'state': '1_new',
        })

    def test_appraisal_creation(self):
        self.assertEqual(self.appraisal.state, '1_new')
        self.assertEqual(self.appraisal.employee_id, self.employee)
        self.assertEqual(self.appraisal.manager_ids, self.manager)
        self.assertEqual(self.appraisal.appraisal_template_id, self.template)

    def test_action_confirm(self):
        self.appraisal.action_confirm()
        self.assertEqual(self.appraisal.state, '2_pending')
        self.assertFalse(self.appraisal.employee_feedback_published)
        self.assertFalse(self.appraisal.manager_feedback_published)
        self.assertEqual(len(self.appraisal.activity_ids), 2)

    def test_action_done(self):
        self.appraisal.action_confirm()
        self.appraisal.action_done()
        self.assertEqual(self.appraisal.state, '3_done')
        self.assertTrue(self.appraisal.employee_feedback_published)
        self.assertTrue(self.appraisal.manager_feedback_published)

    def test_publish_employee_feedback_toggle(self):
        published = self.appraisal.employee_feedback_published
        self.appraisal.action_publish_employee_feedback()
        self.assertNotEqual(self.appraisal.employee_feedback_published, published)

    def test_publish_manager_feedback_toggle(self):
        published = self.appraisal.manager_feedback_published
        self.appraisal.action_publish_manager_feedback()
        self.assertNotEqual(self.appraisal.manager_feedback_published, published)

    def test_default_template_assigned(self):
        self.assertEqual(self.appraisal.appraisal_template_id, self.template)
        self.assertEqual(self.appraisal.employee_feedback, self.template.appraisal_employee_feedback_template)
        self.assertEqual(self.appraisal.manager_feedback, self.template.appraisal_manager_feedback_template)