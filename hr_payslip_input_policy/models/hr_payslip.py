# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    @api.multi
    def _get_input_from_contract(self):
        for payslip in self:
            for payslip_input in payslip.input_line_ids:
                payslip_input._get_input_from_contract()

    @api.multi
    def compute_sheet(self):
        super(HrPayslip, self).compute_sheet()
        self._get_input_from_contract()


class HrPayslipInput(models.Model):
    _inherit = "hr.payslip.input"

    @api.multi
    def _get_input_from_contract(self):
        self.ensure_one()
        obj_contract_input = self.env[
            "hr.contract.input_type"]
        criteria = [
            ("contract_id", "=", self.contract_id.id),
            ("input_type_id.code", "=", self.code),
        ]
        contract_input = obj_contract_input.search(
            criteria, limit=1)
        if contract_input:
            self.amount = contract_input.amount
