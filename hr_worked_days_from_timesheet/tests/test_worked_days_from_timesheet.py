# -*- coding: utf-8 -*-
# © 2012 Odoo Canada
# © 2015 Acysos S.L.
# © 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase
import time


class TestComputeWorkdays(TransactionCase):

    def setUp(self):
        super(TestComputeWorkdays, self).setUp()

        self.company = self.env.ref('base.main_company')
        self.user_admin = self.env.ref('base.partner_root')
        self.timesheet_sheet = self.env['hr_timesheet_sheet.sheet']
        self.project_2 = self.env.ref('project.project_project_2')

        # create user
        user_dict = {
            'name': 'User 1',
            'login': 'tua@example.com',
            'password': 'base-test-passwd',
        }
        self.user_test = self.env['res.users'].create(user_dict)

        # create Employee
        employee_dict = {
            'name': 'Employee 1',
            'user_id': self.user_test.id,
            'address_id': self.user_test.partner_id.id,
        }
        self.employee = self.env['hr.employee'].create(employee_dict)

        # create Contract
        contract_dict = {
            'name': 'Contract 1',
            'employee_id': self.employee.id,
            'wage': 10.0,
        }
        self.contract = self.env['hr.contract'].create(contract_dict)

        self.timesheet_sheet = self.timesheet_sheet.create({
            'date_from': time.strftime('%Y-%m-11'),
            'date_to': time.strftime('%Y-%m-17'),
            'name': 'Employee 1',
            'state': 'new',
            'user_id': self.user_test.id,
            'employee_id': self.employee.id,
        })

        # I add 5 hours of work timesheet
        self.timesheet_sheet.write({'timesheet_ids': [(0, 0, {
            'project_id': self.project_2.id,
            'date': time.strftime('%Y-%m-11'),
            'name': 'Develop UT for hr module(1)',
            'user_id': self.user_test.id,
            'unit_amount': 5.00,
        })]})

        self.timesheet_sheet.action_timesheet_confirm()
        self.timesheet_sheet.action_timesheet_done()

    def test_timesheet_import(self):
        payslip_dict = {
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'date_from': time.strftime('%Y-%m-01'),
            'date_to': time.strftime('%Y-%m-21'),
        }
        payslip = self.env['hr.payslip'].create(
            payslip_dict)

        payslip.import_worked_days()
        self.assertEqual(payslip.worked_days_line_ids.number_of_hours, 5.0)
