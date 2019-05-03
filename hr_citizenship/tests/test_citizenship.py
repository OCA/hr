# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import SavepointCase
from psycopg2 import IntegrityError


class TestCitizenship(SavepointCase):

    post_install = True
    at_install = False

    def setUp(self):
        super(TestCitizenship, self).setUp()
        self.ctz_model = self.env['res.citizenship']
        self.country_model = self.env['res.country']
        self.applicant = self.env.ref("hr_recruitment.hr_case_salesman0")

        for x in range(5):
            self.ctz_model.create({
                "identification_id": x + 42,
                "country_id": self.country_model.browse(x + 1).id,
                "passport_id": x + 100500,
                "applicant_id": self.applicant.id
            })

    def test_appropriate_recs_moving(self):
        """
        test case when employee created from applicant receive all data
        about citizenship and properly updated
        """
        item_1 = self.applicant.citizenship_ids[2]
        # add priority to one item
        item_1.sequence = 1
        self.applicant.create_employee_from_applicant()
        new_empl = self.applicant.emp_id
        self.assertEqual(len(self.applicant.citizenship_ids), 5)
        self.assertEqual(len(new_empl.citizenship_ids), 5)
        new_empl._compute_passport_data()
        # prioritized item writes in directly in employee card fields
        self.assertEqual(new_empl.identification_id, u'44')
        self.assertEqual(new_empl.passport_id, u'100502')
        self.assertEqual(
            new_empl.country_id.id,
            item_1.country_id.id
        )
        # change in widget trigger updating in card
        item_2 = new_empl.citizenship_ids[3]
        item_3 = new_empl.citizenship_ids[4]
        # simulate wizard update
        vals = {u'citizenship_ids': [
            [1, item_1.id, {u'sequence': 2}],
            [1, item_2.id, {u'sequence': 1}],
            [1, item_3.id, {u'sequence': 3}],
        ]}
        new_empl.write(vals)
        new_empl._compute_passport_data()
        self.assertEqual(new_empl.identification_id, u'45')
        self.assertEqual(new_empl.passport_id, u'100503')
        self.assertEqual(
            new_empl.country_id.id,
            item_2.country_id.id
        )

    def test_create_citizenhip(self):
        with self.assertRaises(IntegrityError):
            self.ctz_model.create({
                "identification_id": 5435,
                "country_id": self.country_model.browse(1).id,
                "passport_id": 100500,
            })
