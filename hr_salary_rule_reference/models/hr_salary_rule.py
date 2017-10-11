# -*- coding: utf-8 -*-
# Copyright 2013 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    @api.multi
    def _compute_rule(self, localdict):
        self.ensure_one()

        # Add reference to the rule itself
        localdict['rule'] = self

        # The payslip contained in the local dict is an object that is
        # different from an actual payslip. The real payslip is
        # contained in the attribute 'dict' of that object.
        payslip = localdict['payslip']
        if not isinstance(payslip, type(self.env['hr.payslip'])):
            payslip = payslip.dict
            payslip.refresh()
            localdict['payslip'] = payslip

        # Pass the rule_id parameter, because the parent function
        # has a not standard signature
        return super(HrSalaryRule, self)._compute_rule(localdict)
