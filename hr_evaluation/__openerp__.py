# -*- coding: utf-8 -*-
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

{
    'name': 'Employee Appraisals',
    'summary': 'Periodical Evaluations, Appraisals, Surveys',
    'version': '9.0.1.0.0',
    'author': 'OpenERP SA, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'website': 'https://github.com/OCA/hr',
    'depends': ['hr', 'calendar', 'survey'],
    "data": [
        'security/ir.model.access.csv',
        'security/hr_evaluation_security.xml',
        'views/hr_evaluation_view.xml',
        'report/hr_evaluation_report_view.xml',
        'views/survey_data_appraisal.xml',
        'views/hr_evaluation_data.xml',
        'views/hr_evaluation_installer.xml',
    ],
    "demo": ["demo/hr_evaluation_demo.xml"],
    'installable': True,
    'application': True,
}
