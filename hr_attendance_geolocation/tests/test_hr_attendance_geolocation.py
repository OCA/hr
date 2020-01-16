# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2019 Eficent Business and IT Consulting Services S.L..
#    All Rights Reserved.
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


class TestHrAttendanceGeolocation(TransactionCase):

    def setUp(self):
        super(TestHrAttendanceGeolocation, self).setUp()
        self.hr_attendance_model = self.env['hr.attendance']
        self.hr_employee_model = self.env['hr.employee']
        self.employee = self.hr_employee_model.create({
            'name': 'Employee A',
        })
        self.location = [41.3910970, 2.1548569]

    def test_attendance_geolocation(self):
        context = {'attendance_location': self.location}
        self.employee.with_context(context).attendance_action_change()
        attendances = self.hr_attendance_model.search([
            ('employee_id', '=', self.employee.id)])
        self.assertEqual(
            len(attendances), 1, "One attendance should have been created")
        self.assertEqual(
            attendances[0].latitude, self.location[0])
        self.assertEqual(
            attendances[0].longitude, self.location[1])
