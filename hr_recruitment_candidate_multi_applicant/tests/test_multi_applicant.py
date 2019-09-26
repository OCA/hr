# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests import common


class TestApplicant(common.TransactionCase):

        def setUp(self):
            super(TestApplicant, self).setUp()
            self.hr_applicant = self.env['hr.applicant']
            self.toto = self.hr_applicant.create({
                'name': 'Toto',
                'email_from': 'toto@camptocamp.com',
            })
            self.toto2 = self.hr_applicant.create({
                'name': 'Toto2',
                'email_from': 'toto@camptocamp.com',
            })
            self.jdoe = self.hr_applicant.create({
                'name': 'John Doe',
                'email_from': 'jdoe@camptocamp.com',
            })

        def test_compute_same_email(self):
            self.assertEqual(1, self.toto.same_candidate_application_count)
            self.assertEqual(1, self.toto2.same_candidate_application_count)
            self.assertEqual(0, self.jdoe.same_candidate_application_count)

        def test_same_phone(self):
            self.assertEqual(1, self.toto.same_candidate_application_count)
            self.assertEqual(1, self.toto2.same_candidate_application_count)
            self.assertEqual(0, self.jdoe.same_candidate_application_count)

        def test_action_view_applicants(self):
            ''' Test if we have the right number of applicants in the action'''
            res_action = self.toto.action_view_applicants()
            applicants = self.hr_applicant.search_count(res_action['domain'])
            self.assertEqual(1, applicants)
