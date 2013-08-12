#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyrigth (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
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

import time
from datetime import datetime

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT
from report import report_sxw

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)

        self.localcontext.update({
            'time': time,
            'get_no': self.get_no,
            'get_basic':self.get_basic,
            'get_ot':self.get_ot,
            'get_transportation': self.get_transportation,
            'get_allowances': self.get_allowances,
            'get_gross':self.get_gross,
            'get_taxable_gross': self.get_taxable_gross,
            'get_ded_fit': self.get_ded_fit,
            'get_ded_pf_ee': self.get_ded_pf_ee,
            'get_deduct': self.get_deduct,
            'get_total_deduct':self.get_total_deduct,
            'get_net':self.get_net,
            'get_er_contributions': self.get_er_contributions,
            'get_details_by_payslip': self.get_details_by_payslip,
        })
        self.no = 0
        self.salary = 0.0
        self.ot = 0.0
        self.transportation = 0.0
        self.allowances = 0.0
        self.gross = 0.0
        self.taxable_gross = 0.0
        self.ded_fit = 0.0
        self.ded_pf_ee = 0.0
        self.deduct = 0.0
        self.total_deduct = 0.0
        self.net = 0.0
        self.er_contributions = 0.0
        self.saved_run_id = -1

    def _reset_values(self, run_id):
        self.no = 0
        self.salary = 0.0
        self.ot = 0.0
        self.transportation = 0.0
        self.allowances = 0.0
        self.gross = 0.0
        self.taxable_gross = 0.0
        self.ded_fit = 0.0
        self.ded_pf_ee = 0.0
        self.deduct = 0.0
        self.total_deduct = 0.0
        self.net = 0.0
        self.er_contributions = 0.0
        self.saved_run_id = run_id

    def get_details_by_payslip(self, payslips):
        
        res = []
        for slip in payslips:
            if self.saved_run_id != slip.payslip_run_id.id:
                self._reset_values(slip.payslip_run_id.id)
                
            tmp = self.get_details_by_rule_category(slip.details_by_salary_rule_category)
            tmp['name'] = slip.employee_id.name
            tmp['id_no'] = slip.employee_id.f_employee_no
            res.append(tmp)
        return res
    
    # Most of this function (except at the end) is copied verbatim from
    # the Pay Slip Details Report
    #
    def get_details_by_rule_category(self, obj):
        payslip_line = self.pool.get('hr.payslip.line')
        rule_cate_obj = self.pool.get('hr.salary.rule.category')

        def get_recursive_parent(rule_categories):
            if not rule_categories:
                return []
            if rule_categories[0].parent_id:
                rule_categories.insert(0, rule_categories[0].parent_id)
                get_recursive_parent(rule_categories)
            return rule_categories

        res = []
        result = {}
        ids = []

        # Choose only the categories (or rules) that we want to
        # show in the report.
        #
        regline = {
            'name': '',
            'id_no': '',
            'salary': 0,
            'ot': 0,
            'transportation': 0,
            'allowances': 0,
            'taxable_gross': 0,
            'gross': 0,
            'fit': 0,
            'ee_pension': 0,
            'deductions': 0,
            'deductions_total': 0,
            'net': 0,
            'er_contributions': 0,
        }
        
        # Arrange the Pay Slip Lines by category
        #
        for id in range(len(obj)):
            ids.append(obj[id].id)
        if ids:
            self.cr.execute('''SELECT pl.id, pl.category_id FROM hr_payslip_line as pl \
                LEFT JOIN hr_salary_rule_category AS rc on (pl.category_id = rc.id) \
                WHERE pl.id in %s \
                GROUP BY rc.parent_id, pl.sequence, pl.id, pl.category_id \
                ORDER BY pl.sequence, rc.parent_id''',(tuple(ids),))
            for x in self.cr.fetchall():
                result.setdefault(x[1], [])
                result[x[1]].append(x[0])
            for key, value in result.iteritems():
                rule_categories = rule_cate_obj.browse(self.cr, self.uid, [key])
                parents = get_recursive_parent(rule_categories)
                category_total = 0
                for line in payslip_line.browse(self.cr, self.uid, value):
                    category_total += line.total
                level = 0
                for parent in parents:
                    res.append({
                        'rule_category': parent.name,
                        'name': parent.name,
                        'code': parent.code,
                        'level': level,
                        'total': category_total,
                    })
                    level += 1
                for line in payslip_line.browse(self.cr, self.uid, value):
                    res.append({
                        'rule_category': line.name,
                        'name': line.name,
                        'code': line.code,
                        'total': line.total,
                        'level': level
                    })
            
            for r in res:
                # Level 0 is the category
                if r['code'] == 'BASIC' and r['level'] == 0:
                    regline['salary'] = r['total']
                elif r['code'] == 'OT':
                    regline['ot'] = r['total']
                elif r['code'] == 'TRA' or r['code'] == 'TRVA':
                    regline['transportation'] = r['total']
                elif r['code'] == 'ALW':
                    regline['allowances'] = r['total']
                elif r['code'] == 'TXBL':
                    regline['taxable_gross'] = r['total']
                elif r['code'] == 'GROSS':
                    regline['gross'] = r['total']
                elif r['code'] == 'FITCALC':
                    regline['fit'] = r['total']
                elif r['code'] == 'PENFEE':
                    regline['ee_pension'] = r['total']
                elif r['code'] == 'DED':
                    regline['deductions'] = r['total']
                elif r['code'] == 'DEDTOTAL':
                    regline['deductions_total'] = r['total']
                elif r['code'] == 'NET':
                    regline['net'] = r['total']
                elif r['code'] == 'ER':
                    regline['er_contributions'] = r['total']
            
            # Make adjustments to subtract from the parent category's total the
            # amount of individual rules that we show separately on the sheet.
            #
            regline['allowances'] -= regline['transportation']
            regline['deductions'] -= regline['ee_pension']
            
            # Increase running totals
            #
            self.salary += regline['salary']
            self.ot += regline['ot']
            self.transportation += regline['transportation']
            self.allowances += regline['allowances']
            self.gross += regline['gross']
            self.taxable_gross += regline['taxable_gross']
            self.ded_fit += regline['fit']
            self.ded_pf_ee += regline['ee_pension']
            self.deduct += regline['deductions']
            self.total_deduct += regline['deductions_total']
            self.net += regline['net']
            self.er_contributions += regline['er_contributions']
        
        return regline
    
    def get_basic(self,obj):
        return self.salary

    def get_ot(self,obj):
        return self.ot

    def get_transportation(self,obj):
        return self.transportation

    def get_allowances(self,obj):
        return self.allowances

    def get_gross(self,obj):
        return self.gross

    def get_taxable_gross(self,obj):
        return self.taxable_gross

    def get_ded_fit(self, obj):
        return self.ded_fit
    
    def get_ded_pf_ee(self, obj):
        return self.ded_pf_ee
    
    def get_deduct(self,obj):
        return self.deduct

    def get_total_deduct(self,obj):
        return self.total_deduct

    def get_net(self,obj):
        return self.net

    def get_er_contributions(self, obj):
        return self.er_contributions

    def get_no(self):
        self.no += 1
        return self.no
