# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia <https://opensynergy-indonesia.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestComputeWorkdays(TransactionCase):

    def setUp(self):
        super(TestComputeWorkdays, self).setUp()

        self.company = self.env.ref('base.main_company')
        self.analytic_journal = self.env.ref('hr_timesheet.analytic_journal')
        self.user_admin = self.env.ref('base.partner_root')

        user_dict = {
            'name': 'User 1',
            'login': 'tua@example.com',
            'password': 'base-test-passwd',
        }
        self.user_test = self.env['res.users'].create(user_dict)

        employee_dict = {
            'name': 'Employee 1',
            'user_id': self.user_test.id,
            'journal_id': self.analytic_journal.id,
            'address_id': self.user_test.partner_id.id,
        }
        self.employee = self.env['hr.employee'].create(employee_dict)

        contract_dict = {
            'name': 'Contract 1',
            'employee_id': self.employee.id,
            'wage': 0.0,
        }
        self.contract = self.env['hr.contract'].create(contract_dict)

        analytic_dict = {
            'name': 'Account 1',
            'type': 'normal',
            'use_timesheets': True,
        }

        self.analytic = self.env['account.analytic.account'].create(
            analytic_dict)

        ts1_dict = {
            'employee_id': self.employee.id,
            'date_from': '2014-01-01',
            'date_to': '2014-01-01',
        }
        self.ts1 = self.env['hr_timesheet_sheet.sheet'].create(ts1_dict)

        ts2_dict = {
            'employee_id': self.employee.id,
            'date_from': '2014-01-02',
            'date_to': '2014-01-04',
        }
        self.ts2 = self.env['hr_timesheet_sheet.sheet'].create(ts2_dict)

        ts3_dict = {
            'employee_id': self.employee.id,
            'date_from': '2014-01-05',
            'date_to': '2014-01-15',
        }
        self.ts3 = self.env['hr_timesheet_sheet.sheet'].create(ts3_dict)

        ts4_dict = {
            'employee_id': self.employee.id,
            'date_from': '2014-01-16',
            'date_to': '2014-01-16',
        }
        self.ts4 = self.env['hr_timesheet_sheet.sheet'].create(ts4_dict)

        analytic_ts1_dict = {
            'date': '2014-01-01',
            'user_id': self.user_test.id,
            'name': 'ddd',
            'account_id': self.analytic.id,
            'unit_amount': 3.0,
            'journal_id': self.analytic_journal.id,
        }
        self.analytic_ts1 = self.env['hr.analytic.timesheet'].with_context(
            user_id=self.user_test.id).create(
                analytic_ts1_dict)

        analytic_ts2_dict = {
            'date': '2014-01-02',
            'user_id': self.user_test.id,
            'name': 'ddd',
            'account_id': self.analytic.id,
            'unit_amount': 5.0,
            'journal_id': self.analytic_journal.id,
            'sheet_id': self.ts2.id,
        }
        self.analytic_ts2 = self.env['hr.analytic.timesheet'].with_context(
            user_id=self.user_test.id).create(
                analytic_ts2_dict)

        analytic_ts3_dict = {
            'date': '2014-01-04',
            'user_id': self.user_test.id,
            'sheet_id': self.ts2.id,
            'name': 'ddd',
            'account_id': self.analytic.id,
            'unit_amount': 7.0,
            'journal_id': self.analytic_journal.id,
        }
        self.analytic_ts3 = self.env['hr.analytic.timesheet'].with_context(
            user_id=self.user_test.id).create(
                analytic_ts3_dict)

        analytic_ts4_dict = {
            'date': '2014-01-15',
            'user_id': self.user_test.id,
            'sheet_id': self.ts4.id,
            'name': 'ddd',
            'account_id': self.analytic.id,
            'unit_amount': 11.5,
            'journal_id': self.analytic_journal.id,
        }
        self.analytic_ts4 = self.env['hr.analytic.timesheet'].with_context(
            user_id=self.user_test.id).create(
                analytic_ts4_dict)

        analytic_ts5_dict = {
            'date': '2014-01-16',
            'user_id': self.user_test.id,
            'sheet_id': self.ts1.id,
            'name': 'ddd',
            'account_id': self.analytic.id,
            'unit_amount': 13,
            'journal_id': self.analytic_journal.id,
        }
        self.analytic_ts5 = self.env['hr.analytic.timesheet'].with_context(
            user_id=self.user_test.id).create(
                analytic_ts5_dict)

        ts = self.ts1 + self.ts2 + self.ts3 + self.ts4
        ts.button_confirm()
        ts.signal_workflow('done')

    def test_timesheet_import(self):
        payslip_dict = {
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'date_from': '2014-01-02',
            'date_to': '2014-01-15',
        }
        payslip = self.env['hr.payslip'].create(
            payslip_dict)
        payslip.import_worked_days()
        for wd in payslip.worked_days_line_ids:
            self.assertIn(wd.number_of_hours, [11.5, 12])

        payslip.import_worked_days()
        self.assertEqual(len(payslip.worked_days_line_ids), 2)
