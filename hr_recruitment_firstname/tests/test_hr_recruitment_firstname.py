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


class TestRecruitmentFirstname(TransactionCase):

    def setUp(self):
        super(TestRecruitmentFirstname, self).setUp()
        self.employee_model = self.env['hr.employee']
        self.applicant_model = self.env['hr.applicant']
        self.job_01 = self.env.ref('hr.job_consultant')
        self.partner_01 = self.env.ref('base.res_partner_address_4')
        self.applicant_01 = self.applicant_model.create(
            {'name': 'TEST', 'partner_name': 'lastname',
             'partner_firstname': 'firstname',
             'job_id': self.job_01.id})
        self.applicant_02 = self.applicant_model.create(
            {'name': 'TEST',
             'partner_id': self.partner_01.id,
             'job_id': self.job_01.id})

    def test_applicant_firstname_lastname(self):
        # I create an employee from the applicant
        self.applicant_01.create_employee_from_applicant()
        # I ensure an employee is created
        self.assertTrue(self.applicant_01.emp_id.id is not False)
        # I check lastname and firstname of the created employee
        self.assertEqual(self.applicant_01.emp_id.lastname,
                         self.applicant_01.partner_name)
        self.assertEqual(self.applicant_01.emp_id.firstname,
                         self.applicant_01.partner_firstname)

    def test_applicant_partner(self):
        # I create an employee from the applicant
        self.applicant_02.create_employee_from_applicant()
        # I ensure an employee is created
        self.assertTrue(self.applicant_02.emp_id.id is not False)
        # I check lastname and firstname of the created employee
        self.assertEqual(self.applicant_02.emp_id.lastname,
                         self.applicant_02.partner_id.lastname)
        self.assertEqual(self.applicant_02.emp_id.firstname,
                         self.applicant_02.partner_id.firstname)
