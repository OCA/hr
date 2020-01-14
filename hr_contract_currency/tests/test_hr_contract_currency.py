# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import common


class TestHrContractCurrency(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.today = fields.Date.today()
        self.Contract = self.env['hr.contract']

    def test_1(self):
        contract = self.Contract.create({
            'name': 'Contract #1',
            'wage': 5000.0,
            'date_start': self.today,
            'date_end': self.today,
        })

        self.assertEqual(
            contract.currency_id,
            self.env.company.currency_id
        )
