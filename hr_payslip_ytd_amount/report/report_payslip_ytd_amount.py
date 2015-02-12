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

from openerp.report import report_sxw


class payslip_ytd_amount_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(payslip_ytd_amount_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_payslip_lines': self.get_payslip_lines,
        })

    def get_payslip_lines(self, objects, context=None):
        payslip_lines = self.pool.get('hr.payslip.line').browse(
            self.cr, self.uid, [obj.id for obj in objects], context=context)

        return [
            line for line in payslip_lines
            if line.appears_on_payslip and line.amount
        ]

report_sxw.report_sxw(
    'report.payslip_ytd_amount', 'hr.payslip',
    'hr_payslip_ytd_amount/report/report_payslip_ytd_amount.rml',
    parser=payslip_ytd_amount_report)
