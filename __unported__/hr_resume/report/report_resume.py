# -*- encoding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import time
from report import report_sxw


class report_resume(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_resume, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_experience_by_category': self.get_experience_by_category,
        })

    def get_experience_by_category(self, employee_id, category):
        self.cr.execute(
            "SELECT exp.name, exp.start_date, exp.expire, exp.end_date, "
            "exp.location, exp.certification, "
            "exp.description, exp.diploma, exp.study_field, "
            "part.name partner_name FROM hr_experience exp "
            "LEFT JOIN res_partner part ON part.id = exp.partner_id "
            "WHERE exp.employee_id = %d AND exp.category = '%s'"
            % (employee_id, category))
        return self.cr.dictfetchall()

report_sxw.report_sxw(
    'report.hr.resume.report',
    'hr.employee',
    'addons/hr_resume/report/report_resume.rml',
    parser=report_resume,
    header=False
)
