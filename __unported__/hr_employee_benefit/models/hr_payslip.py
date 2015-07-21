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

from openerp.osv import orm, fields


PAYS_PER_YEAR = {
    'annually': 1,
    'semi-annually': 2,
    'quaterly': 4,
    'bi-monthly': 6,
    'monthly': 12,
    'semi-monthly': 24,
    'bi-weekly': 26,
    'weekly': 52,
    'daily': 365,
}


class HrPayslip(orm.Model):
    _inherit = 'hr.payslip'

    def _get_pays_per_year(
        self, cr, uid, ids, field_name=False, args=False, context=None
    ):
        res = {}

        for payslip in self.browse(cr, uid, ids, context=context):
            contract = payslip.contract_id

            res[payslip.id] = PAYS_PER_YEAR.get(
                contract.schedule_pay, False)

        return res

    _columns = {
        'benefit_line_ids': fields.one2many(
            'hr.payslip.benefit.line',
            'payslip_id',
            'Employee Benefits',
            readonly=True, states={'draft': [('readonly', False)]},
        ),
        # Field required to compute benefits based on an annual amount
        'pays_per_year': fields.function(
            _get_pays_per_year,
            string='Number of pays per year', readonly=True, type='integer',
            store={
                'hr.payslip': (
                    lambda self, cr, uid, ids, c=None: ids,
                    ['contract_id'], 10),
            },
        ),
    }

    def _search_benefits(self, cr, uid, payslip, context=None):
        return payslip.contract_id.benefit_line_ids

    def button_compute_benefits(self, cr, uid, ids, context=None):
        for payslip in self.browse(cr, uid, ids, context=context):
            payslip.compute_benefits(payslip)

    def compute_benefits(self, cr, uid, ids, context=None):
        """
        Compute the employee benefits on the payslip.

        This method can be called from inside a salary rule.

        Exemple
        -------
        payslip.compute_benefits()

        This is required when the benefits are based on the value
        of one or more salary rules.

        The module hr_employee_benefit_percent implements that
        functionnality.
        """
        if isinstance(ids, (int, long)):
            ids = [ids]

        assert len(ids) == 1

        payslip = self.browse(cr, uid, ids[0], context=context)

        payslip.refresh()

        for benefit_line in payslip.benefit_line_ids:
            if benefit_line.source == 'contract':
                benefit_line.unlink()

        benefits = self._search_benefits(
            cr, uid, payslip, context=context)

        benefit_ids = [b.id for b in benefits]

        # Compute the amounts for each employee benefit
        self.pool['hr.employee.benefit'].compute_amounts(
            cr, uid, benefit_ids, payslip, context=context)
