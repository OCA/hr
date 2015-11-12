# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests.common import TransactionCase


class TestDepartment(TransactionCase):

    def setUp(self):
        super(TestDepartment, self).setUp()
        # Get registries
        self.user_model = self.env["res.users"]
        self.department_model = self.env["hr.department"]
        # Get context
        self.context = self.user_model.context_get()
        self.vals = {
            'name': 'test',
            'code': 'TEST',
            'sequence': 1,
        }

    def test_create_department(self):
        department_id = self.department_model.create(self.vals)
        self.assertEqual(self.vals['name'], department_id.name)
        self.assertEqual(self.vals['code'], department_id.code)
        self.assertEqual(self.vals['sequence'], department_id.sequence)

    def test_name_search_department(self):
        department_id = self.department_model.create(self.vals)

        found_id = self.department_model.\
            name_search(name=self.vals['name'])[0][0]
        self.assertEqual(department_id.id, found_id,
                         "Found wrong id for name=%s" % self.vals['name'])
