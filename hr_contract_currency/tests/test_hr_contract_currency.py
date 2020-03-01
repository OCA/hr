# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import common


class TestHrContractCurrency(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.today = fields.Date.today()
        self.now = fields.Datetime.now()
        self.Employee = self.env['hr.employee']
        self.SudoEmployee = self.Employee.sudo()
        self.Contract = self.env['hr.contract']
        self.SudoContract = self.Contract.sudo()

    def test_1(self):
        employee = self.SudoEmployee.create({
            'name': 'Employee #1',
            'contract_ids': [
                (0, 0, {
                    'name': 'Employee #1 Contract #1',
                    'wage': 5000.0,
                    'date_start': self.today,
                    'date_end': self.today,
                }),
            ],
        })

        self.assertEqual(
            employee.contract_id.currency_id,
            self.env.user.company_id.currency_id
        )

    def test_2(self):
        my_company = self.env['res.company'].create({
            'name': 'My Company',
            'currency_id': self.env.ref("base.CHF").id,
        })
        contract = self.Contract.create({
            'name': 'Contract #2',
            'wage': 1000.0,
            'date_start': self.today,
            'date_end': self.today,
            'company_id': my_company.id,
        })

        self.assertEqual(
            contract.currency_id,
            self.env.ref("base.CHF")
        )
        self.assertNotEqual(
            contract.currency_id,
            self.env.user.company_id.currency_id
        )
