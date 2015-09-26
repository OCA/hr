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

from openerp import api, models, fields


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'
    exemption_id = fields.Many2one(
        'hr.income.tax.exemption',
        'Exemption',
    )

    @api.multi
    def compute_rule(self, rule_id, localdict):
        if self.exemption_id and self.check_exemption(localdict):
            return (0, 0, 0)

        return super(HrSalaryRule, self).compute_rule(
                rule_id, localdict, context=context)

    @api.multi
    def check_exemption(self, localdict):
        """ Check whether the employee is exempted for the given rule
        """

        assert len(self) == 1, 'must be called with a single employee'

        return localdict['employee'].exempted_from(
            self.exemption_id, localdict['payslip'].date_to)
