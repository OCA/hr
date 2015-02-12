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
            'translate_term': self.translate_in_employee_lang,
        })

        self.employee_lang_dict = {}

        payslips = self.pool['hr.payslip'].browse(
            cr, uid, context.get('active_ids'), context=context)

        for payslip in payslips:
            employee = payslip.employee_id

            user = employee.user_id

            if employee.id not in self.employee_lang_dict:
                if not user:
                    # If the employee has no user, take the user that
                    # requested the report
                    user = self.employee_lang_dict[employee.id] = \
                        self.pool['res.users'].browse(
                            cr, uid, uid, context=context)

                self.employee_lang_dict[employee.id] = user.lang

    def get_payslip_lines(self, objects, context=None):
        payslip_lines = self.pool.get('hr.payslip.line').browse(
            self.cr, self.uid, [obj.id for obj in objects], context=context)

        return [
            line for line in payslip_lines
            if line.appears_on_payslip and line.amount
        ]

    def translate_in_employee_lang(self, term, payslip, is_payslip_line=False):
        """
        Get the translated term in the employee's language
        """
        lang = self.employee_lang_dict[payslip.employee_id.id]

        translation_model = self.pool.get('ir.translation')

        if is_payslip_line:
            # Translate a payslip line name
            translation_ids = translation_model.search(
                self.cr, self.uid, [
                    ('lang', '=', lang),
                    ('value', '!=', ''),
                    ('src', '=', term),
                ], context=self.localcontext)
        else:
            # Translate a label in the report
            translation_ids = translation_model.search(
                self.cr, self.uid, [
                    ('type', '=', 'report'),
                    ('name', '=', 'payslip_ytd_amount'),
                    ('lang', '=', lang),
                    ('value', '!=', ''),
                    ('src', '=', term),
                ], context=self.localcontext)

        if translation_ids:
            translation = translation_model.browse(
                self.cr, self.uid, translation_ids[0],
                context=self.localcontext)

            return translation.value

        return term

report_sxw.report_sxw(
    'report.payslip_ytd_amount', 'hr.payslip',
    'hr_payslip_ytd_amount/report/report_payslip_ytd_amount.rml',
    parser=payslip_ytd_amount_report)
