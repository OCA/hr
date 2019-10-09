# -*- coding: utf-8 -*-
##############################################################################
#
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
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
from ..init_hook import pre_init_hook, post_init_hook
from openerp.tests.common import TransactionCase


class TestHrEmployeeDataFromWorkAddress(TransactionCase):
    def test_hooks(self):
        pre_init_hook(self.env.cr)
        post_init_hook(self.env.cr, self.env.registry)

    def test_create_write(self):
        user1 = self.env['res.users'].create({
            'name': 'user1',
            'login': 'user1',
        })
        employee = self.env['hr.employee'].create({
            'name': 'employee',
            'address_id': self.env['res.partner'].create({
                'name': 'partner1',
            }).id,
            'user_id': user1.id,
        })
        # user1's partner_id must be replaced by the employee's work address
        self.assertEqual(user1.partner_id, employee.address_id)
        # if we assign a new user, the same should happen
        user2 = self.env['res.users'].create({
            'name': 'user2',
            'login': 'user2',
        })
        employee.write({'user_id': user2.id})
        self.assertEqual(user2.partner_id, employee.address_id)

    def test_onchange(self):
        result = self.env.ref('hr.employee_fp').onchange_company(
            self.env.ref('base.main_company').id)
        self.assertFalse('address_id' in result.get('value', {}))
        result = self.env.ref('hr.employee_fp').onchange_address_id(
            self.env.ref('base.main_partner').id)
        self.assertFalse('work_phone' in result.get('value', {}))
        self.assertFalse('mobile_phone' in result.get('value', {}))
