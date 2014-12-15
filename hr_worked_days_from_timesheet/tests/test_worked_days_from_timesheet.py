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


class test_worked_days_from_timesheet(common.TransactionCase):
    def setUp(self):
        super(test_worked_days_from_timesheet, self).setUp()
        self.employee_model = self.registry('hr.employee')
        self.user_model = self.registry("res.users")
        self.payslip_model = self.registry("hr.payslip")
        self.worked_days_model = self.registry("hr.payslip.worked_days")
        self.contract_model = self.registry("hr.contract")
        self.ts_sheet_model = self.registry("hr_timesheet_sheet.sheet")
        self.timesheet_model = self.registry("hr.analytic.timesheet")
        self.structure_model = self.registry("hr.payroll.structure")
        self.account_model = self.registry("account.analytic.account")
        self.slip_run_model = self.registry("hr.payslip.run")
        self.run_wizard_model = self.registry("hr.payslip.employees")
        self.journal_model = self.registry("account.analytic.journal")

        self.context = self.user_model.context_get(self.cr, self.uid)

        cr, uid, context = self.cr, self.uid, self.context

        # Create two user
        self.user_id = self.user_model.create(
            cr, uid, {
                'name': 'User 1',
                'login': 'test',
                'password': 'test',
            }, context=context)
        self.user_2_id = self.user_model.create(
            cr, uid, {
                'name': 'User 2',
                'login': 'test_2',
                'password': 'test_2',
            }, context=context)

        # Create two employee
        self.employee_id = self.employee_model.create(
            cr, uid, {
                'name': 'Employee 1',
                'user_id': self.user_id,
            }, context=context)

        self.employee_2_id = self.employee_model.create(
            cr, uid, {
                'name': 'Employee 2',
                'user_id': self.user_2_id,
            }, context=context)

        self.structure_id = self.structure_model.search(
            cr, uid, [('code', '=', 'BASE')], context=context)[0]

        # Create two contract for the employee
        self.contract_id = self.contract_model.create(
            self.cr, self.uid,
            {
                'employee_id': self.employee_id,
                'name': 'Contract 1',
                'wage': 50000,
                'date_start': '2014-01-01',
                'struct_id': self.structure_id,
            },
            context=context)

        # Create two contract for the employee
        self.contract_2_id = self.contract_model.create(
            cr, uid, {
                'employee_id': self.employee_2_id,
                'name': 'Contract 1',
                'wage': 50000,
                'date_start': '2014-01-01',
                'struct_id': self.structure_id,
            },
            context=context)

        # Create an analytic account
        self.account_id = self.account_model.create(
            cr, uid, {
                'name': 'Account 1',
                'type': 'normal',
                'use_timesheets': True,
            },
            context=context)

        # Create timesheets
        self.ts_sheet_ids = [
            self.ts_sheet_model.create(
                cr, uid,
                {
                    'employee_id': ts[0],
                    'date_from': ts[1],
                    'date_to': ts[2],
                },
                context=context,
            ) for ts in [
                (self.employee_id, '2014-01-01', '2014-01-01'),
                (self.employee_id, '2014-01-02', '2014-01-04'),
                (self.employee_id, '2014-01-05', '2014-01-15'),
                (self.employee_id, '2014-01-16', '2014-01-16'),
                (self.employee_2_id, '2014-01-05', '2014-01-15'),
            ]
        ]

        self.journal_id = self.journal_model.search(
            cr, uid, [('code', '=', 'TS')], context=context)[0]

        self.timesheet_ids = [
            self.timesheet_model.create(
                cr, uid, {
                    'date': ts[0],
                    'user_id': ts[1],
                    'name': 'ddd',
                    'account_id': self.account_id,
                    'unit_amount': ts[2],
                    'journal_id': self.journal_id,
                },
                context=context,
            ) for ts in [
                ('2014-01-01', self.user_id, 3),
                ('2014-01-02', self.user_id, 5),
                ('2014-01-04', self.user_id, 7),
                ('2014-01-15', self.user_id, 11.5),
                ('2014-01-16', self.user_id, 1),
                ('2014-01-05', self.user_2_id, 13),
            ]
        ]

        self.ts_sheet_model.write(
            cr, uid, self.ts_sheet_ids, {'state': 'done'}, context=context)

    def tearDown(self):
        cr, uid, context = self.cr, self.uid, self.context

        self.ts_sheet_model.write(
            cr, uid, self.ts_sheet_ids, {'state': 'draft'}, context=context)
        self.timesheet_model.unlink(
            cr, uid, self.timesheet_ids, context=context)

        self.ts_sheet_model.unlink(
            cr, uid, self.ts_sheet_ids, context=context)

        self.contract_model.unlink(
            cr, uid, [self.contract_id, self.contract_2_id], context=context)

        self.employee_model.unlink(
            cr, uid, [self.employee_id, self.employee_2_id], context=context)

        self.user_model.unlink(
            cr, uid, [self.user_id, self.user_2_id], context=context)

        super(test_worked_days_from_timesheet, self).tearDown()

    def test_import_worked_days(self):
        """
        Test the payslip method import_worked_days
        when there is approved timesheets for the pay period
        """
        cr, uid, context = self.cr, self.uid, self.context
        self.payslip_id = self.payslip_model.create(
            cr, uid, {
                'employee_id': self.employee_id,
                'contract_id': self.contract_id,
                'date_from': '2014-01-02',
                'date_to': '2014-01-15',
            }, context=context)

        self.payslip_model.import_worked_days(
            cr, uid, [self.payslip_id], context=context)

        payslip = self.payslip_model.browse(
            cr, uid, self.payslip_id, context=context)

        sum_wd = 0
        for wd in payslip.worked_days_line_ids:
            sum_wd += wd.number_of_hours

        # 23.5 hours should be computed
        # 5 hours for timesheet 2
        # 7 hours timesheet 3
        # 11.5 hours for timesheet 4
        self.assertEqual(sum_wd, 5 + 7 + 11.5)

        # Test again to verify that old records get erased
        # as the function is called a second time
        self.payslip_model.import_worked_days(
            cr, uid, [self.payslip_id], context=context)

        self.assertEqual(len(payslip.worked_days_line_ids), 2)

        self.payslip_model.unlink(
            cr, uid, [self.payslip_id], context=context)

    def test_payslip_batch_compute_sheet(self):
        """
        Test payslip_emlpoyees method compute_sheet
        when import_from_timesheet is False
        The method should behave the same as without this module.
        """
        cr, uid, context = self.cr, self.uid, self.context

        # Create a payslip batch
        self.slip_run_id = self.slip_run_model.create(
            cr, uid, {
                'name': 'test',
                'date_start': '2014-01-02',
                'date_end': '2014-01-15',
            }, context=context)

        self.wizard_id = self.run_wizard_model.create(
            cr, uid, {
                'employee_ids': [(
                    6, 0, [self.employee_id, self.employee_2_id])],
                'import_from_timesheet': False,
            }, context=context
        )

        wizard_context = context.copy()
        wizard_context['active_id'] = self.slip_run_id

        self.run_wizard_model.compute_sheet(
            cr, uid, [self.wizard_id], context=wizard_context)

        slip_run = self.slip_run_model.browse(
            cr, uid, self.slip_run_id, context=context)

        # Check that one payslip was created for each employee,
        # that worked_days were not imported entered and that
        # the payslips were computed
        self.assertEqual(len(slip_run.slip_ids), 2)

        for slip in slip_run.slip_ids:
            self.assertEqual(len(slip.worked_days_line_ids), 0)
            # If the payslip was computed, it should have lines
            self.assertNotEqual(len(slip.line_ids), 0)

        self.payslip_model.unlink(
            cr, uid,
            [slip.id for slip in slip_run.slip_ids],
            context=context)

        self.slip_run_model.unlink(
            cr, uid, [self.slip_run_id], context=context)

    def test_payslip_batch_compute_sheet_import_worked_days(self):
        """
        Test payslip_emlpoyees method compute_sheet
        when import_from_timesheet is True
        """
        cr, uid, context = self.cr, self.uid, self.context

        # Create a payslip batch
        self.slip_run_id = self.slip_run_model.create(
            cr, uid, {
                'name': 'test',
                'date_start': '2014-01-02',
                'date_end': '2014-01-15',
            }, context=context)

        self.wizard_id = self.run_wizard_model.create(
            cr, uid, {
                'employee_ids': [(
                    6, 0, [self.employee_id, self.employee_2_id])],
                'import_from_timesheet': True,
            }, context=context
        )

        wizard_context = context.copy()
        wizard_context['active_id'] = self.slip_run_id

        self.run_wizard_model.compute_sheet(
            cr, uid, [self.wizard_id], context=wizard_context)

        slip_run = self.slip_run_model.browse(
            cr, uid, self.slip_run_id, context=context)

        # Check that one payslip was created for each employee,
        # that worked_days were imported and that the payslips were
        # computed
        self.assertEqual(len(slip_run.slip_ids), 2)

        for slip in slip_run.slip_ids:
            self.assertNotEqual(len(slip.line_ids), 0)

        for slip in slip_run.slip_ids:
            if slip.employee_id.id == self.employee_id:
                employee_1_slip = slip

        sum_wd = 0
        for wd in employee_1_slip.worked_days_line_ids:
            sum_wd += wd.number_of_hours

        # 23.5 hours should be computed
        # 5 hours for timesheet 2
        # 7 hours timesheet 3
        # 11.5 hours for timesheet 4
        self.assertEqual(sum_wd, 5 + 7 + 11.5)

        self.payslip_model.unlink(
            cr, uid,
            [slip.id for slip in slip_run.slip_ids],
            context=context)

        self.slip_run_model.unlink(
            cr, uid, [self.slip_run_id], context=context)
