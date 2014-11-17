# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Codekaki Systems (<http://codekaki.com>).
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
    'name': 'Duty Roster',
    'version': '0.1',
    'category': 'Human Resources',
    'description': """
Duty Roster
===========
This module allows easy encoding of duty roster that is usually created and
distributed in spreadsheet. It follows the common format used by
manufacturing to enroll their general workers for duty each month.

Shift codes must be defined prior to creation of duty roster.  At the moment,
shift code is exactly 1 letter. While it may seems like a non-ideal
restriction, it allows duty roster to be created very quickly (with the help
of custom widgets).

The creation of a duty roster is usually responsiblity of department
supervisor, and validated by department manager. However, this module does
not distinguish supervisor from manager. User of this module should edit
the groups accordingly.
""",
    'author': "Codekaki Systems",
    'website': 'http://codekaki.com',
    'depends': ['hr'],
    'data': [
        'security/ir.model.access.csv',
        'security/ir.rule.xml',
        'data/hr_shift_code.xml',
        'data/hr_roster.xml',
        'duty_roster_view.xml',
        'duty_roster_workflow.xml',
    ],
    'css': [
        'static/src/css/hr_roster.css',
    ],
    'js': [
        'static/src/js/hr_roster.js',
    ],
    'qweb': [
        'static/src/xml/hr_shift_code.xml',
        'static/src/xml/hr_roster.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
