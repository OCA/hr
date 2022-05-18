# © 2012 Odoo Canada
# © 2015 Acysos S.L.
# © 2017 ForgeFlow S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import time

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestComputeWorkdays(TransactionCase):
    def setUp(self):
        super(TestComputeWorkdays, self).setUp()

        self.company = self.env.ref("base.main_company")
        self.user_admin = self.env.ref("base.partner_root")
        self.timesheet_sheet = self.env["hr_timesheet.sheet"]
        self.project_2 = self.env.ref("project.project_project_2")
        hr_user_group = self.env.ref("hr.group_hr_user")
        self.user_admin.user_id.groups_id = [(4, hr_user_group.id)]

        # create user
        user_dict = {
            "name": "User 1",
            "login": "tua@example.com",
            "password": "base-test-passwd",
        }
        self.user_test = self.env["res.users"].create(user_dict)

        user_dict2 = {
            "name": "User 2",
            "login": "user2@example.com",
            "password": "base-test-passwd",
        }
        self.user_test2 = self.env["res.users"].create(user_dict2)

        # create Employee
        employee_dict = {
            "name": "Employee 1",
            "user_id": self.user_test.id,
            "address_id": self.user_test.partner_id.id,
        }
        self.employee = self.env["hr.employee"].create(employee_dict)

        employee_dict2 = {
            "name": "Employee 2",
            "user_id": self.user_test2.id,
            "address_id": self.user_test.partner_id.id,
        }
        self.employee2 = self.env["hr.employee"].create(employee_dict2)

        # create Contract
        contract_dict = {
            "name": "Contract 1",
            "employee_id": self.employee.id,
            "wage": 10.0,
        }
        self.contract = self.env["hr.contract"].create(contract_dict)

        contract_dict2 = {
            "name": "Contract 1",
            "employee_id": self.employee.id,
            "wage": 15.0,
        }
        self.contract2 = self.env["hr.contract"].create(contract_dict2)

        self.timesheet_sheet = self.timesheet_sheet.create(
            {
                "date_start": fields.Date.to_date(time.strftime("%Y-%m-11")),
                "date_end": fields.Date.to_date(time.strftime("%Y-%m-17")),
                "name": "Employee 1",
                "state": "new",
                "employee_id": self.employee.id,
            }
        )

        # I add 5 hours of work timesheet
        self.timesheet_sheet.write(
            {
                "timesheet_ids": [
                    (
                        0,
                        0,
                        {
                            "project_id": self.project_2.id,
                            "date": fields.Date.to_date(time.strftime("%Y-%m-11")),
                            "name": "Develop UT for hr module(1)",
                            "user_id": self.user_test.id,
                            "unit_amount": 5.00,
                        },
                    )
                ]
            }
        )

        self.timesheet_sheet.action_timesheet_confirm()
        self.timesheet_sheet.sudo().with_user(self.user_admin.id).with_context(
            mail_track_log_only=True
        ).action_timesheet_done()

    def test_timesheet_import(self):
        payslip_dict = {
            "employee_id": self.employee.id,
            "contract_id": self.contract.id,
            "date_from": fields.Date.to_date(time.strftime("%Y-%m-01")),
            "date_to": fields.Date.to_date(time.strftime("%Y-%m-21")),
        }
        payslip = self.env["hr.payslip"].create(payslip_dict)

        payslip.import_worked_days()
        self.assertEqual(payslip.worked_days_line_ids.number_of_hours, 5.0)

    def test_check_contract_warning(self):
        payslip_dict = {
            "employee_id": self.employee.id,
            "date_from": fields.Date.to_date(time.strftime("%Y-%m-01")),
            "date_to": fields.Date.to_date(time.strftime("%Y-%m-21")),
        }
        payslip = self.env["hr.payslip"].create(payslip_dict)
        with self.assertRaises(UserError):
            payslip.import_worked_days()

    def test_get_timesheet_for_employee_warning(self):

        payslip_dict = {
            "employee_id": self.employee2.id,
            "contract_id": self.contract2.id,
            "date_from": fields.Date.to_date(time.strftime("%Y-%m-01")),
            "date_to": fields.Date.to_date(time.strftime("%Y-%m-21")),
        }
        payslip = self.env["hr.payslip"].create(payslip_dict)
        with self.assertRaises(UserError):
            payslip.import_worked_days()
