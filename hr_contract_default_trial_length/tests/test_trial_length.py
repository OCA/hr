# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from odoo.tests.common import TransactionCase


class TestTrialLength(TransactionCase):

    def setUp(self):
        super().setUp()
        self.type1 = self.env['hr.contract.type'].create({
            'name': 'Type 1',
            'trial_length': 20,
        })
        self.type2 = self.env['hr.contract.type'].create({
            'name': 'Type 2',
            'trial_length': 10,
        })
        self.contract = self.env['hr.contract'].create({
            'name': 'Contract',
            'type_id': self.type1.id,
            'date_start': '2019-10-10',
            'wage': 50000,
        })

    def test_onchange_trial_date_start(self):
        self.contract.write({'type_id': self.type2.id})
        self.contract.onchange_trial_date_start()
        self.assertEqual(self.contract.trial_date_end, '2019-10-20')
