# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase
from openerp.exceptions import ValidationError
# pylint: disable=openerp-exception-warning
from openerp.exceptions import Warning


class TestHrEmployeeSpouse(TransactionCase):
    # pylint: disable=invalid-name
    def setUp(self):
        super(TestHrEmployeeSpouse, self).setUp()
        self.employee_model = self.env['hr.employee']
        self.partner_model = self.env['res.partner']
        self.partner1 = self.partner_model.create(
            {
                'name': 'partner1',
                'country_id': self.env.ref('base.nl').id
            }
        )
        self.partner2 = self.partner_model.create(
            {
                'name': 'partner2',
                'country_id': self.env.ref('base.nl').id
            }
        )
        self.partner3 = self.partner_model.create(
            {
                'name': 'partner3',
                'country_id': self.env.ref('base.nl').id
            }
        )
        self.employee1 = self.employee_model.create(
            {
                'name': 'Employee1',
            }
        )

        self.spouse_tag_id = self.env.ref(
            'hr_family.res_partner_category_spouse'
        ).id

    def test_vwn_hr_employee_spouse(self):
        # create new employee with spouse
        self.employee_model.create(
            {
                'name': 'Employee2',
                'partner_spouse_id': self.partner1.id
            }
        )
        # verify spouse tag
        self.assertTrue(self.spouse_tag_id in self.partner1.category_id.ids)
        # new employee with spouse already allocated
        with self.assertRaises(ValidationError):
            self.employee_model.create(
                {
                    'name': 'Employee2',
                    'partner_spouse_id': self.partner1.id
                }
            )
        # modify employee with available spouse
        self.employee1.write({'partner_spouse_id': self.partner2.id})
        # verify spouse tag
        self.assertTrue(self.spouse_tag_id in self.partner2.category_id.ids)
        # modify employee with unavailable spouse (taken)
        with self.assertRaises(ValidationError):
            self.employee1.write({'partner_spouse_id': self.partner1.id})
        # verify spouse tag partner2 still married
        self.assertTrue(self.spouse_tag_id in self.partner2.category_id.ids)
        # verify spouse tag partner1 still married
        self.assertTrue(self.spouse_tag_id in self.partner1.category_id.ids)
        # remove Tag from a spouse
        # TODO if i rename Warning Usererror won't work, read code why?
        with self.assertRaises(Warning):
            self.partner2.write({'category_id': [(5, 0, 0)]})
        # create a partner with spouse tag
        with self.assertRaises(Warning):
            self.partner_model.create({
                'name': 'test_partner',
                'category_id': [(4, self.spouse_tag_id)]
            })
