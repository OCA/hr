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

from openerp.osv import fields, orm


class HrSalaryRule(orm.Model):
    _inherit = 'hr.salary.rule'
    _columns = {
        'exemption_id': fields.many2one(
            'hr.income.tax.exemption',
            'Exemption',
        ),
    }

    def compute_rule(self, cr, uid, rule_id, localdict, context=None):
        rule = self.browse(cr, uid, rule_id, context=context)

        if rule.exemption_id and rule.check_exemption(localdict):
            return (0, 0, 0)

        return super(HrSalaryRule, self).compute_rule(
            cr, uid, rule_id, localdict, context=context)

    def check_exemption(self, cr, uid, ids, localdict, context=None):
        """ Check whether the employee is exempted for the given rule
        """
        if isinstance(ids, (int, long)):
            ids = [ids]

        assert len(ids) == 1, 'must be called with a single employee'

        rule = self.browse(cr, uid, ids[0], context=context)

        return localdict['employee'].exempted_from(
            rule.exemption_id, localdict['payslip'].date_to)
