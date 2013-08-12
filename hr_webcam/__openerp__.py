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
    'name': 'Capture employee picture with webcam',
    'version': '1.0',
    'category': 'Generic Modules/Human Resources',
    'description': """
HR WebCam
=========

Capture employee pictures with an attached web cam.
    """,
    'author':'Michael Telahun Makonnen <mmakonnen@gmail.com>',
    'website':'http://miketelahun.wordpress.com',
    'depends': [
        'hr',
        'web',
    ],
    'js': [
        'static/src/js/jquery.webcam.js',
        'static/src/js/hr_webcam.js',
    ],
    'css': [
        'static/src/css/hr_webcam.css',
    ],
    'qweb': [
        'static/src/xml/hr_webcam.xml',
    ],
    'init_xml': [
    ],
    'update_xml': [
        'hr_webcam_data.xml',
        'hr_webcam_view.xml',
    ],
    'test': [
    ],
    'demo_xml': [
    ],
    'installable': True,
    'active': False,
}