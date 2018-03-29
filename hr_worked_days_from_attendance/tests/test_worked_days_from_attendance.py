# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia <https://opensynergy-indonesia.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from datetime import datetime, timedelta


class TestComputeWorkdays(TransactionCase):

    def setUp(self):
        super(TestComputeWorkdays, self).setUp()

        self.company = self.env.ref('base.main_company')
        self.analytic_journal = self.env.ref('hr_timesheet.analytic_journal')
        self.user_admin = self.env.ref('base.partner_root')
        self.company.update({'timesheet_range': 'month'})

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

        ts_dict = {
            'name': 'Test Timesheet',
            'employee_id': self.employee.id,
            'date_from': '2016-04-01',
            'date_to': '2016-04-30',
        }

        ts_obj = self.env['hr_timesheet_sheet.sheet']
        self.ts = ts_obj.create(ts_dict)

        attn_obj = self.env['hr.attendance']

        day_start = datetime.strptime('2016-04-01', '%Y-%m-%d')
        day_end = datetime.strptime('2016-04-30', '%Y-%m-%d')
        date_start = datetime.strptime(
            '2016-04-01 07:00:00', '%Y-%m-%d %H:%M:%S')
        date_end = datetime.strptime(
            '2016-04-01 17:00:00', '%Y-%m-%d %H:%M:%S')
        self.nb_days = (day_end - day_start).days + 1
        for day in range(0, self.nb_days):

            attn_dict_1 = {
                'sheet_id': self.ts.id,
                'name': date_start.strftime('%Y-%m-%d %H:%M:%S'),
                'employee_id': self.employee.id,
                'action': 'sign_in',
            }
            attn_obj.create(attn_dict_1)

            attn_dict_2 = {
                'sheet_id': self.ts.id,
                'name': date_end.strftime('%Y-%m-%d %H:%M:%S'),
                'employee_id': self.employee.id,
                'action': 'sign_out',
            }
            attn_obj.create(attn_dict_2)
            date_start = date_start + timedelta(days=1)
            date_end = date_end + timedelta(days=1)

    def test_timesheet_import(self):
        wd_obj = self.env['hr.payslip.worked_days']
        payslip_dict = {
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'date_from': '2016-04-01',
            'date_to': '2016-04-30',
        }
        payslip = self.env['hr.payslip'].create(
            payslip_dict)
        payslip.button_import_attendance()

        criteria = [
            ('payslip_id', '=', payslip.id),
            ('code', '=', 'ATTN'),
        ]
        wd = wd_obj.search(criteria)
        wd.ensure_one()
        self.assertEqual(wd[0].number_of_days, 30.0)
