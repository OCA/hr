# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import exceptions
from openerp.tests.common import TransactionCase


class TestHrCategoryParent(TransactionCase):
    def test_hr_employee_category_parent(self):
        with self.assertRaises(exceptions.ValidationError):
            with self.env.cr.savepoint():
                self.env.ref('hr_employee_category_parent.cat3').write({
                    'parent_id':
                    self.env.ref('hr_employee_category_parent.cat3').id,
                })
        with self.assertRaises(exceptions.ValidationError):
            with self.env.cr.savepoint():
                self.env.ref('hr_employee_category_parent.cat1').write({
                    'parent_id':
                    self.env.ref('hr_employee_category_parent.cat3').id,
                })
        self.assertEqual(
            self.env.ref('hr_employee_category_parent.cat3').display_name,
            'Category 1 / Category 2 / Category 3',
        )
