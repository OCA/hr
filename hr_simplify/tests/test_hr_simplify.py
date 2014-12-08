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

from openerp.tests import common


class test_hr_simplify(common.TransactionCase):
    def setUp(self):
        super(test_hr_simplify, self).setUp()
        self.user_model = self.registry("res.users")
        self.employee_model = self.registry("hr.employee")
        self.job_model = self.registry("hr.job")
        self.contract_model = self.registry("hr.contract")
        self.context = self.user_model.context_get(self.cr, self.uid)
        cr, uid, context = self.cr, self.uid, self.context

        self.employee_id = self.employee_model.create(
            cr, uid, {'name': 'Employee 1'}, context=context
        )
        self.job_id = self.job_model.create(
            cr, uid, {'name': 'Job 1'}, context=context
        )
        self.contract_id = self.contract_model.create(
            cr, uid, {
                'name': 'Contract 1',
                'employee_id': self.employee_id,
                'wage': 50000,
                'job_id': self.job_id,
            }, context=context
        )

    def tearDown(self):
        cr, uid, context = self.cr, self.uid, self.context

        self.job_model.unlink(
            cr, uid, [self.job_id], context=context)
        self.contract_model.unlink(
            cr, uid, [self.contract_id], context=context)
        self.employee_model.unlink(
            cr, uid, [self.employee_id], context=context)

        super(test_hr_simplify, self).tearDown()

    def test_no_of_contracts(self):
        """
        Test that _no_of_contracts method on hr_job computes without error
        and returns the number of employee
        """
        cr, uid, context = self.cr, self.uid, self.context

        res = self.job_model._no_of_contracts(
            cr, uid, [self.job_id],
            name='no_of_employee', args=None, context=context
        )

        self.assertTrue(res[self.job_id]['no_of_employee'] == 1)
