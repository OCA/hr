# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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


class TestEmployeeFirstname(TransactionCase):
    def setUp(self):
        super(TestEmployeeFirstname, self).setUp()
        self.employee_model = self.env['hr.employee']

        # Create 3 employees to concatenate the firstname and lastname
        # in name_related
        self.employee1_id = self.employee_model.create(
            {'firstname': 'Jan', 'lastname': 'Van Eyck'})
        self.employee2_id = self.employee_model.create(
            {'firstname': 'Jean-Pierre', 'lastname': 'Carnaud'})
        self.employee3_id = self.employee_model.create(
            {'firstname': 'Famke', 'lastname': 'Jenssens'})

        # Create 3 employees for split the name_related to
        # firstname and lastname
        self.employee10_id = self.employee_model.create(
            {'name': ' Jan Van Eyck', 'firstname': ' ', 'lastname':  ' '})
        self.employee20_id = self.employee_model.create(
            {'name': 'Jean-Pierre Carnaud', 'firstname': ' ', 'lastname': ' '})
        self.employee30_id = self.employee_model.create(
            {'name': 'FamkeJenssens', 'firstname': ' ', 'lastname': ' '})

    def test_get_name(self):
        """
        Validate the _get_name method is concatenating
        the firstname and lastname
        """
        # Check for employee1
        self.assertTrue(self.employee1_id.name_related == 'Jan Van Eyck')

        # Check for employee2
        self.assertTrue(self.employee2_id.name_related == 'Jean-Pierre '
                                                          'Carnaud')

        # Check for employee3
        self.assertTrue(self.employee3_id.name_related == 'Famke Jenssens')

    def test_auto_init_name(self):
        """
        Validate the _auto_init if the name related is split
        in firstname and lastname
        """
        # Check for employee10
        self.assertTrue(self.employee10_id.firstname == "Jan")
        self.assertTrue(self.employee10_id.lastname == 'Van Eyck')

        # Check for employee20
        self.assertTrue(self.employee20_id.firstname == 'Jean-Pierre')
        self.assertTrue(self.employee20_id.lastname == 'Carnaud')

        # Check for employee30
        self.assertTrue(self.employee30_id.firstname == 'FamkeJenssens')
        self.assertTrue(self.employee30_id.lastname == ' ')
