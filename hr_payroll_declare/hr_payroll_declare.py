#!/usr/bin/env python
#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
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

from osv import osv
from osv import fields
from tools import config

class hr_payroll_declar(osv.osv):
    '''
    Decleration Form
    '''
    _name = 'hr.payroll.declare'
    _description = 'Decleration Form'
    
    _columns = {
        'name':fields.char('Name', size=1024, required=False),
        'company_id':fields.many2one('res.company', 'Company', required=True),
        'employee_id':fields.many2one('hr.employee', 'Employee', required=True),
        'income_sal': fields.float('Income by Salary', digits=(16, int(config['price_accuracy'])), readonly=True),
        'income_ids':fields.one2many('hr.payroll.declare.line', 'income_id', 'Source Of Income', required=False),
        'investment_ids':fields.one2many('hr.payroll.declare.line', 'invest_id', 'Investments', required=False),
        'claim_ids':fields.one2many('hr.payroll.declare.line', 'claim_id', 'Allowance to Claime', required=False),
        'date': fields.date('Date'),
        
        'income': fields.float('Taxable Income', digits=(16, int(config['price_accuracy'])), readonly=True),
        'investment': fields.float('Total Investment', digits=(16, int(config['price_accuracy'])), readonly=True),
        'claims': fields.float('Total Allowance Claims', digits=(16, int(config['price_accuracy'])), readonly=True),
        
        'state':fields.selection([
            ('draft','Draft'),
            ('pending','Waiting for Review'),
            ('pending','Approved by HR'),
            ('done','Confirm'),
        ],'State', select=True, readonly=True),
        'note': fields.text('Description'),   
    }
hr_payroll_declar()

class hr_payroll_declare_line(osv.osv):
    '''
    Decleration Line
    '''
    _name = 'hr.payroll.declare.line'
    _description = 'Decleration Line'
    
    _columns = {
        'name':fields.char('Name', size=64, required=False),
        'note': fields.text('Description'),
        'income_id':fields.many2one('hr.payroll.declare', 'Income', required=False),
        'invest_id':fields.many2one('hr.payroll.declare', 'Investment', required=False),
        'claim_id':fields.many2one('hr.payroll.declare', 'Allowance Claims', required=False),
        'amount': fields.float('Amount', digits=(16, int(config['price_accuracy']))),
    }
hr_payroll_declare_line()
