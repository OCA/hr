# -*- coding: utf-8 -*-
# © 2016 - Eficent http://www.eficent.com/
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
import logging


class TestHrPayslipChangeState(TransactionCase):
    def setUp(self):
        result = super(TestHrPayslipChangeState, self).setUp()
        self.payslip_model = self.registry('hr.payslip')
        self.contract_model = self.registry('hr.contract')
        self.tested_model = self.registry('hr.payslip.change.state')
        return result

    def test_change_state(self):
        cr, uid = self.cr, self.uid
        payslip_model = self.payslip_model
        tested_model = self.tested_model
        contract_id = self.contract_model.create(cr, uid, {'employee_id': 1,
                                                           'name': 'demo',
                                                           'wage': 10000,
                                                           'struck_id': 1})

        payslip_id = payslip_model.create(cr, uid, {'employee_id': 1,
                                                    'name': 'test_payslip',
                                                    'contract_id': contract_id,
                                                    'struck_id': 1})

        action = tested_model.create(cr, uid, {'state': 'verify'})
        context = {'active_ids': [payslip_id]}

        # By default a payslip is on draft state
        tested_model.change_state_confirm(cr, uid, [action], context)

        # trying to set it to wrong states
        try:
            tested_model.write(cr, uid, action, {'state': 'draft'})
            tested_model.change_state_confirm(cr, uid, [action], context)
        except Exception as e:
            wrong_tries = 1
            logging.info('hr_payslip_change_state: ' + str(e))

        # Now the payslip should be computed but in state draft
        payslip = payslip_model.browse(cr, uid, [payslip_id], context)
        self.assertEqual(payslip.state, 'draft')
        self.assertNotEqual(payslip.number, None)
        tested_model.write(cr, uid, action, {'state': 'done'})
        tested_model.change_state_confirm(cr, uid, [action], context)

        # Now the payslip should be confirmed
        self.assertEqual(payslip.state, 'done')

        # trying to set it to wrong states
        try:
            tested_model.write(cr, uid, action, {'state': 'draft'})
            tested_model.change_state_confirm(cr, uid, [action], context)
        except Exception as e:
            wrong_tries += 1
            logging.info('hr_payslip_change_state: ' + str(e))
        try:
            tested_model.write(cr, uid, action, {'state': 'verify'})
            tested_model.change_state_confirm(cr, uid, [action], context)
        except Exception as e:
            wrong_tries += 1
            logging.info('hr_payslip_change_state: ' + str(e))
        try:
            tested_model.write(cr, uid, action, {'state': 'done'})
            tested_model.change_state_confirm(cr, uid, [action], context)
        except Exception as e:
            wrong_tries += 1
            logging.info('hr_payslip_change_state: ' + str(e))

        tested_model.write(cr, uid, action, {'state': 'cancel'})
        tested_model.change_state_confirm(cr, uid, [action], context)

        # Now the payslip should be canceled
        self.assertEqual(payslip.state, 'cancel')

        # trying to set it to wrong states
        try:
            tested_model.write(cr, uid, action, {'state': 'done'})
            tested_model.change_state_confirm(cr, uid, [action], context)
        except Exception as e:
            wrong_tries += 1
            logging.info('hr_payslip_change_state: ' + str(e))
        try:
            tested_model.write(cr, uid, action, {'state': 'verify'})
            tested_model.change_state_confirm(cr, uid, [action], context)
        except Exception as e:
            wrong_tries += 1
            logging.info('hr_payslip_change_state: ' + str(e))
        try:
            tested_model.write(cr, uid, action, {'state': 'cancel'})
            tested_model.change_state_confirm(cr, uid, [action], context)
        except Exception as e:
            wrong_tries += 1
            logging.info('hr_payslip_change_state: ' + str(e))

        tested_model.write(cr, uid, action, {'state': 'draft'})
        tested_model.change_state_confirm(cr, uid, [action], context)
        # again, it shoud be draft. Also checking if wrong changes happened
        self.assertEqual(payslip.state, 'draft')
        self.assertEqual(wrong_tries, 7)
        logging.info(
            '**TEST FINISHED**')
