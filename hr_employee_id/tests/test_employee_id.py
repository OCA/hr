# -*- coding: utf-8 -*-
# © 2015 Salton Massally <smassally@idtlabs.sl>
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common


class TestEmployeeID(common.TransactionCase):

    def setUp(self):
        super(TestEmployeeID, self).setUp()
        self.employee_model = self.env['hr.employee']
        self.company = self.env.ref('base.main_company')
        self.sequence = self.env.ref('hr_employee_id.seq_employeeid_ref')

    def test_random_id_generation(self):
        # test ID generation for random
        employee = self.employee_model.create({'name': 'Employee'})

        self.assertAlmostEqual(len(employee.identification_id), 5)

    def test_random_id_generation_changed_digits(self):
        # test ID generation for random but with defaults changed
        self.company.write({'employee_id_random_digits': 10})
        employee = self.employee_model.create({'name': 'Employee'})

        self.assertAlmostEqual(len(employee.identification_id), 10)

    def test_sequences_id_generation(self):
        # test ID generation for a provided sequence
        self.company.write({'employee_id_gen_method': 'sequence',
                            'employee_id_sequence': self.sequence.id})
        employee = self.employee_model.create({'name': 'Employee'})

        self.assertTrue(len(employee.identification_id))
