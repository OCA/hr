# -*- coding: utf-8 -*-
# © 2016 - Eficent http://www.eficent.com/
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
import logging


class TestHrPayslipChangeState(TransactionCase):
    def setUp(self):
        result = super(TestHrPayslipChangeState, self).setUp()
        self.payslip_model = self.env['hr.payslip']
        self.contract_model = self.env['hr.contract']
        self.tested_model = self.env['hr.payslip.change.state']
        return result

    def test_change_state(self):
        payslip_model = self.payslip_model
        tested_model = self.tested_model
        contract_id = self.contract_model.create({'employee_id': 1,
                                                  'name': 'demo',
                                                  'wage': 10000,
                                                  'struck_id': 1})

        payslip_id = payslip_model.create({'employee_id': 1,
                                           'name': 'test_payslip',
                                           'contract_id': contract_id,
                                           'struck_id': 1})

        action = tested_model.create({'state': 'verify'})
        context = {'active_ids': [payslip_id]}

        # By default a payslip is on draft state
        tested_model.change_state_confirm([action], context)

        # trying to set it to wrong states
        with self.assertRaises(UserWarning):
            tested_model.write(action, {'state': 'draft'})
            tested_model.change_state_confirm([action], context)

        # Now the payslip should be computed but in state draft
        payslip = payslip_model.browse([payslip_id], context)
        self.assertEqual(payslip.state, 'draft')
        self.assertNotEqual(payslip.number, None)
        tested_model.write(action, {'state': 'done'})
        tested_model.change_state_confirm([action], context)

        # Now the payslip should be confirmed
        self.assertEqual(payslip.state, 'done')

        # trying to set it to wrong states
        with self.assertRaises(UserWarning):
            tested_model.write(action, {'state': 'draft'})
            tested_model.change_state_confirm([action], context)
        with self.assertRaises(UserWarning):
            tested_model.write(action, {'state': 'verify'})
            tested_model.change_state_confirm([action], context)
        with self.assertRaises(UserWarning):
            tested_model.write(action, {'state': 'done'})
            tested_model.change_state_confirm([action], context)

        tested_model.write(action, {'state': 'cancel'})
        tested_model.change_state_confirm([action], context)

        # Now the payslip should be canceled
        self.assertEqual(payslip.state, 'cancel')

        # trying to set it to wrong states
        with self.assertRaises(UserWarning):
            tested_model.write(action, {'state': 'done'})
            tested_model.change_state_confirm([action], context)
        with self.assertRaises(UserWarning):
            tested_model.write(action, {'state': 'verify'})
            tested_model.change_state_confirm([action], context)
        with self.assertRaises(UserWarning):
            tested_model.write(action, {'state': 'cancel'})
            tested_model.change_state_confirm([action], context)

        tested_model.write(action, {'state': 'draft'})
        tested_model.change_state_confirm([action], context)
        # again, it shoud be draft. Also checking if wrong changes happened
        self.assertEqual(payslip.state, 'draft')
        logging.info(
            '**TEST FINISHED**')
