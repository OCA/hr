# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from report import report_sxw
import datetime
import mx.DateTime

class candidate_summary(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(candidate_summary, self).__init__(cr, uid, name, context)
        self.localcontext.update( {
            'time': time,
            'get_education': self._get_education,
            'get_scheduled_date':self._get_schedule_date,
        })
        
    def _get_education(self, edu_type):
        edu_list = [("be_ce","BE Computers"),("be_it","BE IT"),("bsc_it","BSc IT"),("bca","BCA"),("btech_ce","BTech Computers"),("btech_it","BTech IT"),("mca","MCA"),("msc_it","MSc IT"),("mtech_ce","MTech Computers"),("other","Other")]
        edu = [x[1] for x in edu_list if x[0]==str(edu_type) ]
        return edu[0]
    
    def _get_schedule_date(self, sch_time):
        if len(sch_time) > 5:
            dt = mx.DateTime.strptime(str(sch_time),"%m/%d/%Y %H:%M:%S")
            sch_dt = dt.strftime('%B %d,%Y at %H:%M %p')
        else :
            sch_dt=""
        return sch_dt

report_sxw.report_sxw('report.candidate.summary', 'hr.interview', 'addons/hr_interview/report/candidate_summary.rml',parser=candidate_summary,header=False)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

