# -*- coding: utf-8 -*-
# © 2015 Eficent
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.osv import fields, orm


class HrPayslipAccountReport(orm.Model):
    _inherit = "hr.payslip.account.report"

    _columns = {
        'hr_period_id': fields.many2one('hr.period', 'HR Payroll Period',
                                        required=False, readonly=True)
    }

    def _select(self):
        select_str = super(HrPayslipAccountReport, self)._select()
        new_select_str = """, p.hr_period_id as hr_period_id"""
        select_str.join(new_select_str)
        return select_str

    def _group_by(self):
        group_by_str = super(HrPayslipAccountReport, self)._group_by()
        new_group_by_str = """, p.hr_period_id"""
        group_by_str.join(new_group_by_str)
        return group_by_str
