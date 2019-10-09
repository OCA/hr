# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class PayslipCase(TransactionCase):

    def setUp(self, *args, **kwargs):
        result = super(PayslipCase, self).setUp(*args, **kwargs)
        self.payslip_obj = self.env['hr.payslip']
        self.run_obj = self.env['hr.payslip.run']
        self.wzd_obj = self.env['hr.payslip.employees']
        self.journal = self.env.ref('account.expenses_journal')

        self.employee = self.env.ref('hr.employee_qdp')
        self.period_3 = self.env.ref('account.period_3')
        self.period_4 = self.env.ref('account.period_4')

        return result

    def _prepare_payslip_data(self):
        data = {
            'employee_id': self.employee.id,
            'contract_id': self.employee.contract_id.id,
            'date_from': self.period_4.date_start,
            'date_to': self.period_4.date_stop,
            'move_date': self.period_3.date_stop,
        }
        return data

    def _prepare_payslip_run_data(self):
        data = {
            'name': self.period_4.name,
            'date_start': self.period_4.date_start,
            'date_end': self.period_4.date_stop,
            'move_date': self.period_3.date_stop,
            'journal_id': self.journal.id,
        }

        return data

    def test_payslip_1(self):
        data = self._prepare_payslip_data()
        payslip = self.payslip_obj.create(data)
        payslip.onchange_move_date()
        self.assertEqual(payslip.period_id.id, self.period_3.id)
        self.assertIsNotNone(payslip)
        self.assertEqual(payslip.state, 'draft')
        payslip.compute_sheet()
        payslip.signal_workflow('hr_verify_sheet')
        self.assertEqual(payslip.state, 'done')
        self.assertIsNotNone(payslip.move_id)
        self.assertEqual(
            payslip.move_id.date,
            self.period_3.date_stop)
        self.assertEqual(
            payslip.move_id.period_id.id,
            self.period_3.id)

    def test_payslip_run_1(self):
        data = self._prepare_payslip_run_data()
        run = self.run_obj.create(data)
        data_wzd = {
            'employee_ids': [(6, 0, [self.employee.id])],
        }
        wzd = self.wzd_obj.with_context(active_id=run.id).create(data_wzd)
        wzd.compute_sheet()
        self.assertEqual(len(run.slip_ids), 1)
