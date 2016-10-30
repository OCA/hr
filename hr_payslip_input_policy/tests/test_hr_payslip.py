# -*- coding: utf-8 -*-
# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class HrPayslip(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(HrPayslip, self).setUp(*args, **kwargs)
        self.obj_type = self.env[
            "hr.payslip.input_type"]
        self.obj_contract = self.env[
            "hr.contract"]
        self.obj_contract_input_type = self.env[
            "hr.contract.input_type"]
        self.obj_rule = self.env[
            "hr.salary.rule"]
        self.obj_struct = self.env[
            "hr.payroll.structure"]
        self.obj_payslip = self.env[
            "hr.payslip"]
        self.rule_categ = self.env.ref(
            "hr_payroll.ALW")
        self.employee = self.env.ref(
            "hr.employee")
        self.type1 = self.obj_type.create({
            "code": "X1",
            "name": "Example 1",
        })
        self.type2 = self.obj_type.create({
            "code": "X2",
            "name": "Example 2",
        })
        compute1 = "result = inputs.X1 and inputs.X1.amount or 0.0"
        self.rule1 = self.obj_rule.create({
            "name": "X Rule 1",
            "code": "X1",
            "category_id": self.rule_categ.id,
            "condition_select": "none",
            "amount_select": "code",
            "amount_python_compute": compute1,
            "input_ids": [(0, 0, {"code": "X1", "name": "Example 1"})],
        })
        compute2 = "result = inputs.X2 and inputs.X2.amount or 0.0"
        self.rule2 = self.obj_rule.create({
            "name": "X Rule 2",
            "code": "X2",
            "category_id": self.rule_categ.id,
            "condition_select": "none",
            "amount_select": "code",
            "amount_python_compute": compute2,
            "input_ids": [(0, 0, {"code": "X2", "name": "Example 2"})],
        })
        self.struct = self.obj_struct.create({
            "name": "X1",
            "code": "X1",
            "parent_id": self.env.ref(
                "hr_payroll.structure_base").id,
            "rule_ids": [(6, 0, [self.rule1.id, self.rule2.id])],
        })

    def test_payslip_compute(self):
        contract = self.obj_contract.create({
            "name": "X 1",
            "employee_id": self.employee.id,
            "struct_id": self.struct.id,
            "wage": 777.00,
            "input_type_ids": [
                (0, 0, {"input_type_id": self.type1.id, "amount": 77.0}),
                (0, 0, {"input_type_id": self.type2.id, "amount": 88.0}),
            ],
        })
        payslip = self.obj_payslip.create({
            "employee_id": self.employee.id,
            "contract_id": contract.id,
            "struct_id": self.struct.id,
        })
        onchange = payslip.onchange_employee_id(
            payslip.date_from,
            payslip.date_to,
            self.employee.id,
            contract.id)
        input_data = []
        for inputs in onchange["value"]["input_line_ids"]:
            input_data.append((0, 0, inputs))
        payslip.write({
            "input_line_ids": input_data,
        })
        payslip.compute_sheet()
        self.assertEqual(
            len(payslip.input_line_ids),
            2)
        for payslip_input in payslip.input_line_ids:
            if payslip_input.code == "X1":
                self.assertEqual(
                    payslip_input.amount,
                    77.0)
            elif payslip_input.code == "X2":
                self.assertEqual(
                    payslip_input.amount,
                    88.0)
