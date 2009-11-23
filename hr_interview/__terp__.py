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

{
    'name': 'Human Resources (Interview Evaluation)',
    'version': '1.0',
    'category': 'Generic Modules/Human Resources',
    'description': """
        This module stores all the educational as well as professional details of candidates who appears for interview.While taking an interview, the interviewers can evaluate the candidate's performance on the basis of categories.The Candidate is evaluated bases on different evaluations,which are related to categories.

Example: Candidate X to be evaluated for Y Category(Category reflects to the recruitment criteria). Category Y has several question types:DBMS questions,OOP questions,Communication skills, etc.

    """,
    'author': 'Tiny',
    'website': 'http://www.openerp.com',
    'depends': ['base', 'hr','crm','smtpclient'],
    'init_xml': [],
    'update_xml': ['hr_interview_view.xml','hr_workflow.xml','hr_sequence.xml','security/ir.model.access.csv','hr_wizard.xml','hr_interview_report.xml'],
    'demo_xml': [],
    'installable': True,
    'active': False,
   
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
