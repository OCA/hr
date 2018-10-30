# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
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
