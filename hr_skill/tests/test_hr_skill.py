# Copyright 2013 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestHrSkill(TransactionCase):

    def test_name_get(self):
        hr_skill_env = self.env['hr.skill']
        soft_skill = hr_skill_env.create({'name': 'Soft skill'})
        leadership_skill = hr_skill_env.create({
            'name': 'Leadership',
            'parent_id': soft_skill.id
        })

        self.assertEqual(
            leadership_skill.name_get(),
            [(leadership_skill.id, 'Soft skill / Leadership')])
