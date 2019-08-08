# Copyright 2015 Savoir-faire Linux. All Rights Reserved.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from . import test_hr_fiscalyear
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class PayslipCase(test_hr_fiscalyear.TestHrFiscalyear):
    def setUp(self):
        result = super(PayslipCase, self).setUp()
        self.payslip_obj = self.env['hr.payslip']
        self.run_obj = self.env['hr.payslip.run']
        self.wzd_obj = self.env['hr.payslip.employees']
        user_id = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'user',
            'email': 'test.user@example.com',
        }).id
        resource_id = self.env['resource.resource'].create({
            'name': 'Test resource',
            'resource_type': 'user',
            'user_id': user_id,
            'company_id': self.company.id
        }).id
        self.employee = self.env['hr.employee'].create({
            'resource_id': resource_id,
            'name': 'Employee 1',
        })
        self.company2 = self.env['res.company'].create({'name': 'Acme'})
        self.type_fy2 = self.create_data_range_type(
            'test_hr_fy', 'fy', self.company2)
        self.type2 = self.create_data_range_type(
            'test_hr_period', 'per', self.company2)
        # create Contract

        self.contract = self.create_contract(
            'Contract 1', 'monthly')
        self.contract2 = self.create_contract(
            'Contract 2', 'quarterly')
        return result

    def create_contract(self, name, schedule_pay):
        contract_dict = {
            'name': name,
            'employee_id': self.employee.id,
            'wage': 10.0,
            'schedule_pay': schedule_pay,
        }
        return self.env['hr.contract'].create(contract_dict)

    def _prepare_payslip_data(self, date_from, date_to, date_payment, company,
                              run=None):
        data = {
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'date_from': date_from,
            'date_to': date_to,
            'date_payment': date_payment,
            'company_id': company.id,
        }
        if run:
            data.update(payslip_run_id=run.id)
        return data

    def _prepare_payslip_run_data(self, period):
        schedule = self.env['hr.payslip.run'].get_default_schedule(
            period.company_id.id)
        data = {
            'name': period.name,
            'date_start': period.date_start,
            'date_end': period.date_end,
            'date_payment': period.date_payment,
            'hr_period_id': period.id,
            'schedule_pay': schedule,
            'company_id': period.company_id.id,
        }
        return data

    def test_payslip(self):
        fy = self.create_fiscal_year({'type_id': self.type_fy.id})
        fy.create_periods()
        periods = self.get_periods(fy)
        fy.button_confirm()
        self.assertEqual(periods[0].state, 'open')
        fy.button_set_to_draft()
        self.assertEqual(periods[0].state, 'draft')
        date_from = periods[1].date_start
        date_to = periods[1].date_end
        move_date = periods[1].date_payment
        company = periods[1].company_id
        data = self._prepare_payslip_data(
            date_from, date_to, move_date, company)
        payslip = self.payslip_obj.create(data)
        payslip.hr_period_id = periods[0]
        payslip.onchange_hr_period_id()
        self.assertEqual(payslip.date_from, periods[0].date_start)
        self.assertEqual(payslip.date_to, periods[0].date_end)
        self.assertEqual(payslip.date_payment, periods[0].date_payment)

        data = self._prepare_payslip_run_data(periods[0])
        run = self.run_obj.create(data)
        run.get_payslip_employees_wizard()
        run.onchange_period_id()
        for pay in run.slip_ids:
            self.assertEqual(pay.date_from, periods[0].date_start)
            self.assertEqual(pay.date_to, periods[0].date_end)
            self.assertEqual(pay.date_payment, periods[0].date_payment)
            with self.assertRaises(UserError):
                periods[1].button_draft()
        for pay in run.slip_ids:
            pay.write({'state': 'draft'})
            with self.assertRaises(UserError):
                run.close_payslip_run()
            pay.write({'state': 'open'})
            pay.hr_payslip.action_payslip_done()
        run.close_payslip_run()
        next_period = fy.search_period(number=periods[0].number + 1)
        self.assertEqual(next_period.state, 'open')
        run.draft_payslip_run()
        for pay in run.slip_ids:
            self.assertEqual(pay.state, 'open')
        self.assertEqual(fy.state, 'open')

    def test_payslip_batch_company(self):
        fy = self.create_fiscal_year({'type_id': self.type_fy.id})
        fy2 = self.create_fiscal_year(
            {'company_id': self.company2.id,
             'date_start': '2016-01-01',
             'date_end': '2016-12-31',
             'type_id': self.type_fy2.id,
             })
        fy.create_periods()
        fy2.create_periods()
        periods = self.get_periods(fy)
        periods2 = self.get_periods(fy2)
        fy.button_confirm()
        fy2.button_confirm()
        self.assertEqual(periods2[0].state, 'open')
        date_from = periods[1].date_start
        date_to = periods[1].date_end
        move_date = periods[1].date_payment
        data = self._prepare_payslip_data(
            date_from, date_to, move_date, self.company)
        self.payslip_obj.create(data)
        data = self._prepare_payslip_run_data(periods[0])
        run = self.run_obj.create(data)
        with self.assertRaises(ValidationError):
            run.write({
                'company_id': self.company2.id})
        run.write({
            'hr_period_id': periods2[0].id,
            'company_id': self.company2.id})
        run.onchange_company_id()
        self.assertEqual(
            run.hr_period_id.date_start.strftime(DF), '2016-01-01')

    def test_contract(self):
        fy = self.create_fiscal_year(
            {'name': 'fy1',
             'company_id': self.company.id,
             'date_start': '2016-01-01',
             'date_end': '2016-12-31',
             'schedule_pay': 'monthly',
             'type_id': self.type_fy.id,
             })
        fy.create_periods()
        fy2 = self.create_fiscal_year(
            {'name': 'fy2',
             'company_id': self.company.id,
             'date_start': '2017-01-01',
             'date_end': '2017-12-31',
             'schedule_pay': 'quarterly',
             'type_id': self.type_fy.id,
             })
        fy2.create_periods()
        periods = self.get_periods(fy)
        fy.button_confirm()
        fy2.button_confirm()
        date_from = periods[1].date_start
        date_to = periods[1].date_end
        move_date = periods[1].date_payment
        run_data = self._prepare_payslip_run_data(periods[1])
        run = self.run_obj.create(run_data)
        data = self._prepare_payslip_data(
            date_from, date_to, move_date, self.company, run)
        payslip = self.payslip_obj.create(data)
        self.assertEqual(payslip.hr_period_id, periods[1], 'Wrong pay period')
        payslip.contract_id = self.contract2
        payslip.onchange_contract_period()
        period = self.env['hr.period'].get_next_period(
            self.company.id, 'quarterly')
        self.assertEqual(payslip.hr_period_id, period)
