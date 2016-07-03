# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from datetime import datetime, timedelta


class TestWorkedDaysFromActivity(TransactionCase):

    def setUp(self, *args, **kwargs):
        result = super(TestWorkedDaysFromActivity, self).setUp(*args, **kwargs)

        self.obj_timesheet = self.env["hr_timesheet_sheet.sheet"]
        self.obj_wd = self.env["hr.payslip.worked_days"]
        self.obj_ts_line = self.env["hr.analytic.timesheet"]

        timesheet_period = self.env.ref("account.period_10")
        timesheet_period_2 = self.env.ref("account.period_11")
        self.employee = self.env.ref("hr.employee")
        self.date_from = timesheet_period.date_start
        self.date_to = timesheet_period.date_stop
        self.date_from_2 = timesheet_period_2.date_start
        self.date_to_2 = timesheet_period_2.date_stop
        self.salary_structure = self.env.ref("hr_payroll.structure_base")
        self.analytic1 = self.env.ref("account.analytic_consultancy")
        self.analytic2 = self.env.ref(
            "account.analytic_super_product_trainings")
        self.analytic3 = self.env.ref("account.analytic_administratif")
        self.rule_base = self.env.ref("hr_payroll.hr_rule_basic")
        self.rule_categ = self.env.ref("hr_payroll.ALW")
        self.product = self.env.ref("product.product_product_consultant")
        self.uom_hour = self.env.ref("product.product_uom_hour")
        self.account = self.env.ref("account.a_expense")
        self.journal = self.env.ref("hr_timesheet.analytic_journal")

        # salary rule for consultancy fee
        self.rule1 = self.env["hr.salary.rule"].create({
            "name": "Allowance for odoo implementor",
            "code": "CONS",
            "timesheet_account_ids": [
                (6, 0, [self.analytic1.id, self.analytic2.id])],
            "category_id": self.rule_categ.id,
        })

        # salary rule for administrative bonuses
        self.rule2 = self.env["hr.salary.rule"].create({
            "name": "Allowance for administrative",
            "code": "ADM",
            "timesheet_account_ids": [(6, 0, [self.analytic3.id])],
            "category_id": self.rule_categ.id,
        })

        # new salary structure for odoo implementor
        self.structure1 = self.env["hr.payroll.structure"].create({
            "name": "Structure of Odoo implementor",
            "code": "ODOO",
            "parent_id": self.salary_structure.id,
            "rule_ids": [(6, 0, [self.rule1.id, self.rule2.id])],
        })

        # contract
        self.contract = self.env["hr.contract"].create({
            "name": "Contract for Administrator",
            "employee_id": self.employee.id,
            "struct_id": self.structure1.id,
            "wage": 0.0,
        })

        # valid timesheet
        self.timesheet1 = self.obj_timesheet.create({
            "employee_id": self.employee.id,
            "date_from": self.date_from,
            "date_to": self.date_to,
        })

        # valid timesheet activities
        self.ts_line1 = self.obj_ts_line.create({
            "name": "Consultancy",
            "user_id": self.employee.user_id.id,
            "date": (datetime.strptime(self.date_from, "%Y-%m-%d") +
                     timedelta(days=7)).strftime("%Y-%m-%d"),
            "unit_amount": 3.0,
            "product_id": self.product.id,
            "product_uom_id": self.uom_hour.id,
            "account_id": self.analytic1.id,
            "amount": 60.0,
            "general_account_id": self.account.id,
            "journal_id": self.journal.id,
        })

        self.ts_line2 = self.obj_ts_line.create({
            "name": "Training",
            "user_id": self.employee.user_id.id,
            "date": (datetime.strptime(self.date_from, "%Y-%m-%d") +
                     timedelta(days=28)).strftime("%Y-%m-%d"),
            "unit_amount": 5.0,
            "product_id": self.product.id,
            "product_uom_id": self.uom_hour.id,
            "account_id": self.analytic2.id,
            "amount": 60.0,
            "general_account_id": self.account.id,
            "journal_id": self.journal.id,
        })

        self.ts_line3 = self.obj_ts_line.create({
            "name": "Administrative",
            "user_id": self.employee.user_id.id,
            "date": (datetime.strptime(self.date_from, "%Y-%m-%d") +
                     timedelta(days=14)).strftime("%Y-%m-%d"),
            "unit_amount": 10.0,
            "product_id": self.product.id,
            "product_uom_id": self.uom_hour.id,
            "account_id": self.analytic3.id,
            "amount": 60.0,
            "general_account_id": self.account.id,
            "journal_id": self.journal.id,
        })

        self.timesheet2 = self.obj_timesheet.create({
            "employee_id": self.employee.id,
            "date_from": self.date_from_2,
            "date_to": self.date_to_2,
        })

        self.ts_line4 = self.obj_ts_line.create({
            "name": "Training",
            "user_id": self.employee.user_id.id,
            "date": (datetime.strptime(self.date_from_2, "%Y-%m-%d") +
                     timedelta(days=28)).strftime("%Y-%m-%d"),
            "unit_amount": 5.0,
            "product_id": self.product.id,
            "product_uom_id": self.uom_hour.id,
            "account_id": self.analytic2.id,
            "amount": 60.0,
            "general_account_id": self.account.id,
            "journal_id": self.journal.id,
        })
        # payslip
        self.payslip = self.env["hr.payslip"].create({
            "employee_id": self.employee.id,
            "contract_id": self.contract.id,
            "date_from": self.date_from,
            "date_to": self.date_to,
        })

        return result

    def test_1(self):
        self.timesheet1.button_confirm()
        self.timesheet1.signal_workflow("done")
        self.timesheet2.button_confirm()
        self.timesheet2.signal_workflow("done")
        self.assertEqual(
            self.timesheet1.state,
            "done")
        self.payslip.compute_sheet()
        self.payslip.action_import_timesheet_activity()
        criteria1 = [
            ("import_from_activity", "=", True),
            ("code", "=", "TSCONS"),
            ("payslip_id", "=", self.payslip.id),
        ]
        wds = self.obj_wd.search(criteria1)
        self.assertEqual(
            len(wds),
            1)
        self.assertEqual(
            wds[0].number_of_hours,
            8.0)
        criteria2 = [
            ("import_from_activity", "=", True),
            ("code", "=", "TSADM"),
            ("payslip_id", "=", self.payslip.id),
        ]
        wds = self.obj_wd.search(criteria2)
        self.assertEqual(
            len(wds),
            1)
        self.assertEqual(
            wds[0].number_of_hours,
            10.0)

    def test_2(self):
        self.payslip.compute_sheet()
        self.payslip.action_import_timesheet_activity()
        criteria1 = [
            ("import_from_activity", "=", True),
            ("code", "=", "TSCONS"),
            ("payslip_id", "=", self.payslip.id),
        ]
        wds = self.obj_wd.search(criteria1)
        self.assertEqual(
            len(wds),
            1)
        self.assertEqual(
            wds[0].number_of_hours,
            0.0)
        criteria2 = [
            ("import_from_activity", "=", True),
            ("code", "=", "TSADM"),
            ("payslip_id", "=", self.payslip.id),
        ]
        wds = self.obj_wd.search(criteria2)
        self.assertEqual(
            len(wds),
            1)
        self.assertEqual(
            wds[0].number_of_hours,
            0.0)
