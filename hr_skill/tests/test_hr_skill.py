# Copyright 2013 Savoir-faire Linux
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestHrSkill(TransactionCase):

    def setUp(self):
        super().setUp()

        self.Employee = self.env['hr.employee']
        self.Skill = self.env['hr.skill']
        self.EmployeeSkill = self.env['hr.employee.skill']

    def test_name_get(self):
        soft_skill = self.Skill.create({
            'name': 'Soft skill',
        })
        leadership_skill = self.Skill.create({
            'name': 'Leadership',
            'parent_id': soft_skill.id
        })

        self.assertEqual(
            leadership_skill.name_get(),
            [(leadership_skill.id, 'Soft skill / Leadership')]
        )

    def test_employee_skills(self):
        skill_a = self.Skill.create({
            'name': 'Skill A',
        })
        skill_b = self.Skill.create({
            'name': 'Skill B',
        })
        skill_c = self.Skill.create({
            'name': 'Skill C',
        })

        employee_a = self.Employee.create({
            'name': 'Employee A',
            'employee_skill_ids': [
                (0, False, {
                    'skill_id': skill_a.id,
                    'level': '0',
                }),
            ],
        })
        employee_ab = self.Employee.create({
            'name': 'Employee A+B',
            'employee_skill_ids': [
                (0, False, {
                    'skill_id': skill_a.id,
                    'level': '0',
                }),
                (0, False, {
                    'skill_id': skill_b.id,
                    'level': '0',
                }),
            ],
        })

        self.assertEqual(
            employee_a | employee_ab,
            self.EmployeeSkill.browse(
                map(
                    lambda x: x[0],
                    self.EmployeeSkill.name_search(skill_a.name)
                )
            ).mapped('employee_id')
        )
        self.assertEqual(
            employee_ab,
            self.EmployeeSkill.browse(
                map(
                    lambda x: x[0],
                    self.EmployeeSkill.name_search(skill_b.name)
                )
            ).mapped('employee_id')
        )
        self.assertEqual(
            self.Employee,
            self.EmployeeSkill.browse(
                map(
                    lambda x: x[0],
                    self.EmployeeSkill.name_search(skill_c.name)
                )
            ).mapped('employee_id')
        )
