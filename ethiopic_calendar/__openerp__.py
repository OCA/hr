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
    'name': 'Ethiopian Calendar',
    'version': '1.0',
    'category': 'Localization',
    'description': """
Date Calculations Based on the Ethiopian Calendar
=================================================

This module provides the pycalcal package developed by Enrico Spinielli. His
implementation is based on 'CALENDRICA 3.0', written by the authors of
'Calendrical Calculations', E. M. Reingold and N. Dershowitz. Other than
providing the pycalcal package it also customizes some objects and their views:
    * Employee - Additional field(s) for inputing Ethiopic date of birth. The Gregorian date is calculated automatically from them.
    """,
    'author':'Michael Telahun Makonnen <mmakonnen@gmail.com>',
    'website':'http://miketelahun.wordpress.com',
    'depends': [
        'hr',
    ],
    'init_xml': [
    ],
    'update_xml': [
        'ethiopic_calendar_view.xml',
    ],
    'test': [
    ],
    'demo_xml': [
    ],
    'installable': True,
    'active': False,
}
