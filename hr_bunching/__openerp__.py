#-*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
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

{
    'name': 'Bunching Performance Recorder',
    'version': '1.0',
    'category': 'Generic Modules/Human Resources',
    'description': """
Record Bunching Records
=======================
This module provides an interface for recording bunching performance of employees
in the grading hall.  Totals, quotas, etc are calculated and the data is integrated
with the payroll system.
    """,
    'author':'Michael Telahun Makonnen <mmakonnen@gmail.com>',
    'website':'http://miketelahun.wordpress.com',
    'depends': [
        'hr',
        'hr_security',
        'l10n_et_hr',
        'report_aeroo',
    ],
    'init_xml': [
    ],
    'update_xml': [
        'security/ir.model.access.csv',
        'report/bunching_sheet.xml',
        'report/bunching_summary.xml',
        'wizard/bunching_sheet.xml',
        'wizard/bunching_sheet_report.xml',
        'wizard/bunching_summary_view.xml',
        'hr_bunching_data.xml',
        'hr_bunching_view.xml',
        'hr_bunching_workflow.xml',
        'res_config_view.xml',
    ],
    'test': [
    ],
    'demo_xml': [
    ],
    'installable': True,
    'active': False,
}
