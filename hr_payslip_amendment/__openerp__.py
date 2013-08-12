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
    'name': 'Pay Slip Amendment',
    'version': '1.0',
    'category': 'Generic Modules/Company Data',
    'author':'Michael Telahun Makonnen <mmakonnen@gmail.com>',
    'description': """
Add Amendments to Current and Future Pay Slips
==============================================
    """,
    'website':'http://miketelahun.wordpress.com',
    'depends': [
        'hr_payroll',
    ],
    'init_xml': [
    ],
    'update_xml': [
        'hr_payslip_amendment_view.xml',
        'hr_payslip_amendment_workflow.xml',
    ],
    'test': [
    ],
    'demo_xml': [
    ],
    'installable': True,
    'active': False,
}
