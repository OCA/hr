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

from openerp.osv import orm


class HrSalaryRule(orm.Model):
    _inherit = 'hr.salary.rule'

    def _filter_benefits(self, cr, uid, ids, payslip, context=None, **kwargs):
        """ Remove all benefits that are exempted from a deduction.
        """
        benefits = super(HrSalaryRule, self)._filter_benefits(
            cr, uid, ids, payslip, context=context, **kwargs)

        rule = self.browse(cr, uid, ids[0], context=context)

        exemption = rule.exemption_id
        if exemption and not rule.employee_benefit_ids:

            benefits = [
                b for b in benefits
                if exemption not in b.category_id.exemption_ids
            ]

        return benefits
