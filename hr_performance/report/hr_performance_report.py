# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
from report import report_sxw
import time
class performance_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(performance_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })
    
report_sxw.report_sxw(
        'report.hr_performance.report', 
        'hr.performance', 
        'addons/hr_performance/report/performance.rml', 
        parser=performance_report,
        header=False
)