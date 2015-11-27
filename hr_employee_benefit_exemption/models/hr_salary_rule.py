# -*- encoding: utf-8 -*-
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

from openerp import api, models


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    @api.multi
    @api.returns('hr.payslip.benefit.line')
    def _filter_benefits(self, payslip, codes=False, **kwargs):
        """ Remove all benefits that are exempted from a deduction.
        """
        benefits = super(HrSalaryRule, self)._filter_benefits(payslip,
                                                              **kwargs)

        rule = self[0]

        exemption = rule.exemption_id
        if exemption and not rule.employee_benefit_ids:

            benefits = [
                b for b in benefits
                if exemption not in b.category_id.exemption_ids
            ]

        return benefits
