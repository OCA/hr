# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    @api.multi
    def compute_rule(self, localdict):
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
        return super(HrSalaryRule, self).compute_rule(self.id, localdict)
