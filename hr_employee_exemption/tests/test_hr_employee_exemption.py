# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Savoir-faire Linux. All Rights Reserved.
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

from openerp.tests import common


class test_hr_employee_exemption(common.TransactionCase):
    def setUp(self):
        super(test_hr_employee_exemption, self).setUp()
        self.employee_model = self.registry('hr.employee')
        self.exemption_model = self.registry('hr.income.tax.exemption')
        self.user_model = self.registry("res.users")

        self.context = self.user_model.context_get(self.cr, self.uid)

        cr, uid, context = self.cr, self.uid, self.context

        self.exemption_1 = self.exemption_model.create(cr, uid, {
            'name': 'Test',
            'code': 'TEST_1',
        }, context=context)

        self.exemption_2 = self.exemption_model.create(cr, uid, {
            'name': 'Test',
            'code': 'TEST_2',
        }, context=context)

        self.employee_id = self.employee_model.create(
            cr, uid, {
                'name': 'Employee 1'
            }, context=context)

    def add_exemption(self, exemption):
        cr, uid, context = self.cr, self.uid, self.context
        employee = self.employee_model.browse(
            cr, uid, self.employee_id, context=context)

        employee.write({'exemption_ids': [(0, 0, {
            'exemption_id': exemption,
            'date_from': '2015-01-01',
            'date_to': '2015-12-31',
        })]})

    def test_exempted_from_no_exemption(self):
        cr, uid, context = self.cr, self.uid, self.context
        employee = self.employee_model.browse(
            cr, uid, self.employee_id, context=context)

        self.assertEqual(employee.exempted_from('TEST_1', '2015-01-01'), False)

    def test_exempted_from_one_exemption(self):
        cr, uid, context = self.cr, self.uid, self.context
        self.add_exemption(self.exemption_1)

        employee = self.employee_model.browse(
            cr, uid, self.employee_id, context=context)

        self.assertEqual(employee.exempted_from('TEST_1', '2015-01-01'), True)
        self.assertEqual(employee.exempted_from('TEST_2', '2015-01-01'), False)

        self.assertEqual(employee.exempted_from('TEST_1', '2014-12-31'), False)
        self.assertEqual(employee.exempted_from('TEST_1', '2015-12-31'), True)
        self.assertEqual(employee.exempted_from('TEST_1', '2016-01-01'), False)

    def test_exempted_from_two_exemption(self):
        cr, uid, context = self.cr, self.uid, self.context
        self.add_exemption(self.exemption_1)
        self.add_exemption(self.exemption_2)

        employee = self.employee_model.browse(
            cr, uid, self.employee_id, context=context)

        self.assertEqual(employee.exempted_from('TEST_1', '2015-01-01'), True)
        self.assertEqual(employee.exempted_from('TEST_2', '2015-01-01'), True)

    def test_exempted_from_no_date_to(self):
        cr, uid, context = self.cr, self.uid, self.context
        employee = self.employee_model.browse(
            cr, uid, self.employee_id, context=context)

        employee.write({'exemption_ids': [(0, 0, {
            'exemption_id': self.exemption_1,
            'date_from': '2015-01-01',
        })]})

        self.assertEqual(employee.exempted_from('TEST_1', '2014-12-31'), False)

        self.assertEqual(employee.exempted_from('TEST_1', '2015-01-01'), True)
        self.assertEqual(employee.exempted_from('TEST_2', '2015-01-01'), False)

        self.assertEqual(employee.exempted_from('TEST_1', '2016-01-01'), True)
        self.assertEqual(employee.exempted_from('TEST_2', '2016-01-01'), False)
