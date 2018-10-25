# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common

from datetime import datetime
from dateutil.relativedelta import relativedelta

_ns = 'hr_employee_relative'


class TestHrEmployeeRelatives(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.Employee = self.env['hr.employee']
        self.EmployeeRelative = self.env['hr.employee.relative']

    def test_age_calculation(self):
        employee = self.Employee.create({
            'name': 'Employee',
            'relative_ids': [
                (0, 0, {
                    'relation_id': self.env.ref(_ns + '.relation_sibling').id,
                    'name': 'Relative',
                    'date_of_birth': datetime.now() + relativedelta(years=-42),
                })
            ],
        })
        relative = self.EmployeeRelative.browse(employee.relative_ids[0].id)
        self.assertEqual(int(relative.age), 42)
