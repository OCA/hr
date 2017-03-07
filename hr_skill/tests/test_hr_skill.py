# -*- coding: utf-8 -*-
# Copyright 2013 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestHrSkill(TransactionCase):

    def test_name_get(self):
        hr_skill_model = self.env['hr.skill']
        soft_skill_id = hr_skill_model.create({'name': 'Soft skill'})
        leadership_skill_id = hr_skill_model.create({
            'name': 'Leadership',
            'parent_id': soft_skill_id.id
        })

        self.assertEqual(
            leadership_skill_id.name_get(),
            [(leadership_skill_id.id, u'Soft skill / Leadership')])
