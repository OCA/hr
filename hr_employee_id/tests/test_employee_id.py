# -*- coding: utf-8 -*-
# © 2015 Salton Massally <smassally@idtlabs.sl>
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


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

    def test_custom_id(self):
        # if we pass the ID no generation occurs.
        # Let's set a sequence and check that is not used at all
        self.company.write({'employee_id_gen_method': 'sequence',
                            'employee_id_sequence': self.sequence.id})
        number = self.sequence.number_next
        employee = self.employee_model.create({
            'name': 'Employee', 'identification_id': 'THERE_YOU_GO'
        })
        self.assertEqual(employee.identification_id, 'THERE_YOU_GO')
        self.assertEqual(self.sequence.number_next, number)

    def test_configuration_default_values(self):
        # test loading of default configuration values
        self.company.write({'employee_id_gen_method': None,
                            'employee_id_random_digits': None,
                            'employee_id_sequence': None})
        config_model = self.env['hr.employeeid.config.settings']
        config = config_model.create({})
        self.assertTrue(config.company_id.id == self.company.id)
        self.assertTrue(config.employee_id_gen_method == 'random')
        self.assertTrue(config.employee_id_random_digits == 5)
        self.assertFalse(config.employee_id_sequence is False)
