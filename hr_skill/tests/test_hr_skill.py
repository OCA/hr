# -*- coding: utf-8 -*-
# © 2018 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp.tools import mute_logger
from openerp.exceptions import except_orm


class TestSkills(TransactionCase):
    """ Test skills """

    def test01_skill_search(self):
        """ Test whether name search also includes categories """
        skill_obj = self.env['hr.skill']

        # There are 6 languages
        results = skill_obj.name_search('Lang')
        self.assertEquals(len(results), 6)
        results = skill_obj.search([('dummy_display_name', 'ilike', 'Lang')])
        self.assertEquals(len(results), 6)
        results = skill_obj.search([('dummy_display_name', '=ilike', '%Lang%')])
        self.assertEquals(len(results), 6)

        # There are 3 European
        results = skill_obj.name_search('Eur')
        self.assertEquals(len(results), 3)
        results = skill_obj.search([('dummy_display_name', 'ilike', 'Eur')])
        self.assertEquals(len(results), 3)
        results = skill_obj.search([('dummy_display_name', '=ilike', '%Eur%')])
        self.assertEquals(len(results), 3)

        # There are two Portuguese, but only one exact Portuguese
        results = skill_obj.name_search('Portuguese')
        self.assertEquals(len(results), 2)
        names = sorted([r[1] for r in results])
        self.assertItemsEqual(names, [
            'Languages / European / Portuguese',
            'Languages / Latin-American / Brazilian Portuguese'
        ])
        results = skill_obj.search([('dummy_display_name', '=', 'Portuguese')])
        self.assertEquals(len(results), 1)

    def test01_skill_workflow(self):
        """ Test create and approve workflow of skills """
        user_demo = self.env.ref('base.user_demo')
        user_root = self.env.ref('base.user_root')
        skill_obj = self.env['hr.skill']
        another_user = user_demo.copy()

        # User can create skill, see it, and edit it
        skill = skill_obj.sudo(user_demo.id).create(dict(name='User skill'))
        self.assertEquals(skill.state, 'pending')
        results = skill_obj.sudo(user_demo.id).name_search('User')
        self.assertEquals(len(results), 1)
        self.assertEquals(skill.create_uid, user_demo)
        self.assertNotEquals(skill.create_uid, another_user)
        skill.sudo(user_demo.id).write(dict(name='User skill modified'))

        # Another user cannot see it
        results = skill_obj.sudo(another_user.id).name_search('User')
        self.assertEquals(len(results), 0)

        # Root can approve it
        skill.sudo(user_root.id).action_approve()

        # Another user can now see it, but not edit it
        results = skill_obj.sudo(another_user.id).name_search('User')
        self.assertEquals(len(results), 1)
        with self.assertRaises(except_orm), mute_logger('openerp.models'):
            skill.sudo(another_user.id).write(dict(name="Garbage"))
