# -*- coding: utf-8 -*-
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

import odoo
from odoo.tests.common import TransactionCase


class TestEmployeeFirstname(TransactionCase):
    def setUp(self):
        super(TestEmployeeFirstname, self).setUp()
        self.employee_model = self.env['hr.employee']

        # Create 3 employees to concatenate the firstname and lastname
        # in name_related
        self.employee1_id = self.employee_model.create(
            {'firstname': 'Jan', 'lastname': 'Van-Eyck'})
        self.employee2_id = self.employee_model.create(
            {'firstname': 'Jean-Pierre', 'lastname': 'Carnaud'})
        self.employee3_id = self.employee_model.create(
            {'firstname': 'Famke', 'lastname': 'Jenssens'})

        # Create 3 employees for split the name_related to
        # firstname and lastname
        self.employee10_id = self.employee_model.create(
            {'name': ' Van-Eyck Jan'})
        self.employee20_id = self.employee_model.create(
            {'name': 'Carnaud Jean-Pierre'})
        self.employee30_id = self.employee_model.create(
            {'name': 'JenssensFamke'})

    def test_get_name(self):
        """
        Validate the _get_name method is concatenating
        the firstname and lastname
        """
        # Check for employee1
        self.assertEqual(self.employee1_id.name, 'Van-Eyck Jan')

        # Check for employee2
        self.assertEqual(self.employee2_id.name, 'Carnaud Jean-Pierre')

        # Check for employee3
        self.assertEqual(self.employee3_id.name, 'Jenssens Famke')

    def test_onchange(self):
        """
        Validate the get_name method is not failing
        """
        field_onchange = self.employee1_id._onchange_spec()
        self.assertEqual(field_onchange.get('firstname'), '1')
        self.assertEqual(field_onchange.get('lastname'), '1')
        values = {'firstname': 'Antonio', 'lastname': 'Esposito'}
        self.employee1_id.onchange(values, 'firstname', field_onchange)
        self.employee1_id.onchange(values, 'lastname', field_onchange)

    def test_auto_init_name(self):
        """
        Validate the create method if the name is split
        in firstname and lastname
        """
        # Check for employee10
        self.assertEqual(self.employee10_id.firstname, 'Jan')
        self.assertEqual(self.employee10_id.lastname, 'Van-Eyck')

        # Check for employee20
        self.assertEqual(self.employee20_id.firstname, 'Jean-Pierre')
        self.assertEqual(self.employee20_id.lastname, 'Carnaud')

        # Check for employee30
        self.assertEqual(self.employee30_id.firstname, False)
        self.assertEqual(self.employee30_id.lastname, 'JenssensFamke')

    def test_change_name(self):
        self.employee1_id.write({'name': 'Carnaud-Eyck Jean-Pierre'})
        self.employee1_id.refresh()

        self.assertEqual(self.employee1_id.firstname, 'Jean-Pierre')
        self.assertEqual(self.employee1_id.lastname, 'Carnaud-Eyck')

    def test_change_name_with_space(self):
        self.employee1_id.write({'name': '  Carnaud-Eyck  Jean-Pierre'})
        self.employee1_id.refresh()

        self.assertEqual(self.employee1_id.firstname, 'Jean-Pierre')
        self.assertEqual(self.employee1_id.lastname, 'Carnaud-Eyck')

    def test_change_firstname(self):
        self.employee1_id.write({'firstname': 'Jean-Pierre'})
        self.employee1_id.refresh()

        self.assertEqual(self.employee1_id.name, 'Van-Eyck Jean-Pierre')

    def test_change_lastname(self):
        self.employee1_id.write({'lastname': 'Carnaud'})
        self.employee1_id.refresh()

        self.assertEqual(self.employee1_id.name, 'Carnaud Jan')

    def test_change_firstname_and_lastname(self):
        self.employee1_id.write({
            'firstname': 'Jean-Pierre',
            'lastname': 'Carnaud'})
        self.employee1_id.refresh()

        self.assertEqual(self.employee1_id.name, 'Carnaud Jean-Pierre')

    @odoo.tests.common.at_install(False)
    @odoo.tests.common.post_install(True)
    def test_update_name_post_install(self):
        self.empl_demo = self.env.ref('hr.employee_root')

        self.assertEqual(self.empl_demo.firstname, 'Parker')
        self.assertEqual(self.empl_demo.lastname, 'Pieter')
