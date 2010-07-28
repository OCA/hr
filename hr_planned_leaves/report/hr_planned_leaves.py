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

import pooler
from report.interface import report_rml
from tools import to_xml
import tools
import datetime
import time
from osv import fields, osv
from report.interface import toxml
from tools.translate import _

class hrself_planned_leaves(report_rml):

    def get_month_name(self, cr, uid, month):
        _months = {1:_("January"), 2:_("February"), 3:_("March"), 4:_("April"), 5:_("May"), 6:_("June"), 7:_("July"), 8:_("August"), 9:_("September"), 10:_("October"), 11:_("November"), 12:_("December")}
        return _months[month]

    def last_day_of_month(self,date):
        if date.month == 12:
            return date.replace(day=31)
        return date.replace(month=date.month+1, day=1) - datetime.timedelta(days=1)

    def date_range(self,start, end):
        r = (end+datetime.timedelta(days=1)-start).days
        return [start+datetime.timedelta(days=i) for i in range(r)]

    def create(self, cr, uid, ids, datas, context):
        emp_obj = pooler.get_pool(cr.dbname).get('hr.employee')
        holidays_obj = pooler.get_pool(cr.dbname).get('hr.holidays')
        holidays_status_obj = pooler.get_pool(cr.dbname).get('hr.holidays.status')
        user_obj = pooler.get_pool(cr.dbname).get('res.users')
        browse_user = user_obj.browse(cr, uid, [uid], context)[0]
        user=browse_user.name
        company=browse_user.company_id.name
        rml="""
        <document filename="Planned Leaves.pdf">
            <template pageSize="29.7cm,21cm" leftMargin="2.0cm" rightMargin="2.0cm" topMargin="2.0cm" bottomMargin="2.0cm" title="Planned Leaves" allowSplitting="20">
                <pageTemplate id="first">
                    <frame id="col1" x1="0.8cm" y1="2.0cm" width="28.0cm" height="17cm"/>
                        <header>
                            <pageGraphics>
                                <setFont name="Helvetica-Bold" size="9"/>
                                <drawString x="1.0cm" y="20.1cm">"""+tools.ustr(company)+"""</drawString>
                                <drawRightString x="28.7cm" y="20.1cm">Planned Leaves</drawRightString>
                                """
        holidays_status_ids=holidays_status_obj.search(cr, uid, [])
        x=10
        for holidays_status in holidays_status_obj.browse(cr,uid,holidays_status_ids):
            rml+="""<place x="%smm" y="-3.20cm"  width="100.0cm" height="5cm">
            <illustration x="%smm" y="-3.00cm" ><fill color="%s"/><rect x="0.0cm" y="-0.38cm" width="%smm" height="0.4cm" fill="yes" stroke="no"/></illustration>
            <para style="status_right"><font color="white">"""%(str(x),str(x),tools.ustr(holidays_status.color_name),len(holidays_status.name)*2)+tools.ustr(holidays_status.name)+"""</font></para></place>"""
            x+=len(holidays_status.name)*2.1
        rml+="""
                                <setFont name="Helvetica" size="9"/>
                                <drawString x="1.0cm" y="1cm">"""+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"""</drawString>
                                <drawString x="14.5cm" y="1cm">"""+tools.ustr(user)+"""</drawString>
                                <drawString x="27.7cm" y="1cm">Page <pageNumber/></drawString>
                                <lineMode width="0.7"/>
                                <lines>1cm 19.7cm 28.7cm 19.7cm</lines>
                                <setFont name="Helvetica" size="8"/>
                            </pageGraphics>
                        </header>
                </pageTemplate>
            </template>
            <stylesheet>
                <blockTableStyle id="month">
                    <blockAlignment value="CENTER" start="1,0" stop="-1,-1" />
                    <blockBackground colorName="#AAAAAA" start="0,0" stop="-1,0"/>
                    <!--lineStyle kind="LINEABOVE" colorName="#000000" start="0,0" stop="-1,-1" />
                    <lineStyle kind="LINEBEFORE" colorName="#000000" start="0,0" stop="-1,-1"/>
                    <lineStyle kind="LINEAFTER" colorName="#000000" start="-1,0" stop="-1,-1"/>
                    <lineStyle kind="LINEBELOW" colorName="#000000" start="0,-1" stop="-1,-1"/-->
                    <blockValign value="TOP"/>
                </blockTableStyle>
                <blockTableStyle id="emp">
                    <blockAlignment value="CENTER" start="1,0" stop="-1,-1" />
                    <!--lineStyle kind="LINEABOVE" colorName="white" start="0,0" stop="-1,-1" />
                    <lineStyle kind="LINEBEFORE" colorName="white" start="0,0" stop="-1,-1"/>
                    <lineStyle kind="LINEAFTER" colorName="white" start="0,0" stop="-1,-1"/>
                    <lineStyle kind="LINEBELOW" colorName="white" start="0,-1" stop="-1,-1"/-->
                    <blockValign value="TOP"/>
                </blockTableStyle>
                <initialize>
                    <paraStyle name="all" alignment="justify"/>
                </initialize>
                <paraStyle name="blank_space" fontName="Helvetica-Bold" fontSize="15.0" leading="19" alignment="CENTER" spaceBefore="12.0" spaceAfter="6.0"/>
                <paraStyle name="employee_name" fontName="Helvetica" fontSize="8.0" leading="10" alignment="LEFT" spaceBefore="0.0" spaceAfter="0.0"/>
                <paraStyle name="terp_default_#" fontName="Times-Roman" fontSize="15.0" leading="0" alignment="LEFT" spaceBefore="0.0" spaceAfter="0.0"/>
                <paraStyle name="status_right" fontName="Helvetica-Bold" fontSize="9.0" leading="11" alignment="LEFT" spaceBefore="6.0" spaceAfter="6.0"/>
                <paraStyle name="days" fontName="Helvetica" fontSize="9.0" leading="11" alignment="LEFT" spaceBefore="0.0" spaceAfter="0.0"/>
                <paraStyle name="month_and_year" fontName="Helvetica-Bold" fontSize="8.0" leading="10" alignment="LEFT" spaceBefore="6.0" spaceAfter="6.0"/>
            </stylesheet>
            <story><para style="blank_space">From : """+ datas['form']['date_from'] +""" To : """+ datas['form']['date_to'] +"""</para>"""
        date_from=time.strptime(datas['form']['date_from'],"%Y-%m-%d")
        date_to=time.strptime(datas['form']['date_to'],"%Y-%m-%d")
        first_date = datetime.date(date_from.tm_year, date_from.tm_mon, date_from.tm_mday)
        last_date = datetime.date(date_to.tm_year, date_to.tm_mon, date_to.tm_mday)
        dateList = self.date_range(first_date, last_date)
        total_years=(date_to.tm_year-date_from.tm_year)+1
        years=[]
        years = [(date_from.tm_year+year) for year in range(0,total_years) if date_from.tm_year+year not in years]
        final_datas=[]
        for year in years:
            for dt in dateList:
                if dt.year==year and {dt.year:{dt.month:[]}} not in final_datas:
                    final_datas.append({dt.year:{dt.month:[]}})
        for data in final_datas:
            for dt in dateList:
                if data.get(dt.year,False) and data[dt.year].keys()[0]==dt.month:
                    data[dt.year][dt.month].append(dt.day)

        for year in years:
            for data in final_datas:
                tmp_total=3.5
                tmp=27.0
                if data.keys()[0]==year:
                    total_days=len(data[year][data[year].keys()[0]])
                    tmp_total+=0.7*total_days
                    Widhts="3.5cm%s"%(',0.7cm'*total_days)
                    _cols_Widhts="%scm%s"%(str(3.5+(tmp-tmp_total)),',0.7cm'*total_days)
                    rml+="""<blockTable colWidths=" """ +tools.ustr(_cols_Widhts) + """ " style="month" repeatRows="1"><tr>"""
                    fdate=tools.ustr(year)+'-'+tools.ustr(data[year].keys()[0])+'-'+tools.ustr(data[year][data[year].keys()[0]][0])
                    ldate=tools.ustr(year)+'-'+tools.ustr(data[year].keys()[0])+'-'+tools.ustr(data[year][data[year].keys()[0]][-1])
                    days=[0,]
                    for day in data[year][data[year].keys()[0]]:
                        days.append(day)
                    for day in days:
                        if day==0:
                           rml+="""<td><para style="month_and_year">"""+ tools.ustr(self.get_month_name(cr, uid, data[year].keys()[0]))+""" - """+tools.ustr(year)+"""</para></td>"""
                        else:
                           rml+="""<td><para style="days">"""+tools.ustr(day)+"""</para></td>"""
                    rml+="""</tr>"""
                    for emp in emp_obj.browse(cr,uid,datas['form']['employee_ids']):
                        rml+="""<tr>"""
                        from_to_lst=[]
                        colors_dict={}
                        holidays_ids=holidays_obj.search(cr, uid, ['&', ('employee_id', '=', emp.id), \
                                                                   '|', '&', ('date_from', '<=', ldate), ('date_to', '>=', fdate), \
                                                                   '&', ('date_from', '>=', fdate), ('date_to', '<=', ldate)])

                        for day in days:
                            if day==0:
                               rml+="""<td><para style="employee_name">"""+ tools.ustr(emp.resource_id.name) +"""</para></td>"""
                            else:
                               if holidays_ids:
                                   for holiday in holidays_obj.browse(cr,uid,holidays_ids):
                                       if holiday.date_from and holiday.date_to:
                                           holiday_date_from=time.strptime(holiday.date_from,"%Y-%m-%d %H:%M:%S")
                                           holiday_date_to=time.strptime(holiday.date_to,"%Y-%m-%d %H:%M:%S")
                                           final_date_from = datetime.date(holiday_date_from.tm_year, holiday_date_from.tm_mon, holiday_date_from.tm_mday)
                                           final_date_to = datetime.date(holiday_date_to.tm_year, holiday_date_to.tm_mon, holiday_date_to.tm_mday)
                                           if data[year].keys()[0]>final_date_from.month:
                                               final_date_from=(self.last_day_of_month(final_date_from)+datetime.timedelta(days=1))
                                           elif final_date_from.month<final_date_to.month:
                                               final_date_to=(self.last_day_of_month(final_date_to)-datetime.timedelta(days=1))
                                           if (final_date_from.day,final_date_to.day) not in from_to_lst:
                                               colors_dict.update({final_date_from.day:str(holiday.holiday_status_id.color_name),final_date_to.day:str(holiday.holiday_status_id.color_name)})
                                               from_to_lst.append((final_date_from.day,final_date_to.day))
                                   leave_days=[]
                                   for from_to in from_to_lst:
                                       leave_days.append(from_to[0])
                                       for j in range(1,(from_to[1]-from_to[0])):
                                           colors_dict.update({from_to[0]+j:colors_dict[from_to[0]]})
                                           leave_days.append(from_to[0]+j)
                                       leave_days.append(from_to[1])
                                   if day in leave_days:
                                       rml+="""
                                       <td>
                                           <illustration>
                                               <fill color="%s"/>
                                               <rect x="-0.33cm" y="-0.50cm" width="0.7 cm" height="0.6cm" fill="yes" stroke="no"/>
                                           </illustration>
                                       </td>"""%(tools.ustr(colors_dict[day]))
                                   else:
                                       rml+="""
                                       <td>
                                           <illustration>
                                               <setFont name="Times-Roman" size="20"/>
                                               <drawString x="-0.20cm" y="-0.43cm">#</drawString>
                                           </illustration>
                                       </td>"""
                               else:
                                   rml+="""
                                   <td>
                                       <illustration>
                                           <setFont name="Times-Roman" size="20"/>
                                           <drawString x="-0.20cm" y="-0.43cm">#</drawString>
                                       </illustration>
                                   </td>"""
                        rml+="""</tr>"""
                    rml+="""</blockTable><para style="blank_space"><font></font></para>"""
        rml+="""</story></document>"""
        report_type = datas.get('report_type', 'pdf')
        create_doc = self.generators[report_type]
        pdf = create_doc(rml, title=self.title)
        return (pdf, report_type)

hrself_planned_leaves('report.hrself.planned.leaves', 'hr.holidays','','')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
