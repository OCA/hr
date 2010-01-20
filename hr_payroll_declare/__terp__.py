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

{
    'name': 'Human Resource Payroll Decleration Form',
    'version': '1.0',
    'category': 'Generic Modules/Human Resources',
    'description': """
    The Payroll Declertion Form - India, Manages,
    * HR Decleration Information, Begining of Financial Year
    * Source of Income
    * List of Claimed Allowances
    * List of Investment
    * Approx Calculated Tax
    """,
    'author': 'Tiny',
    'website': 'http://www.openerp.com',
    'depends': [
        'hr_payroll'
    ],
    'init_xml': [
    ],
    'update_xml': [
        'hr_payroll_declare_view.xml',
    ],
    'demo_xml': [
    ],
    'installable': True,
    'active': False,
}
