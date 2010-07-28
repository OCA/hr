# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    "name" : "Groupe S HR self Report",
    "version" : "1.0",
    "author" : "OpenERP / Groupe S",
    "category" : "Generic Modules/Groupe S",
    "website" : "http://www.openerp.com",
    "description": """Extension of generic HR module for Groupe S needs.""",
    'depends': ['hr_holidays'],
    'update_xml':['wizard/hr_planned_leaves_wizard_view.xml','hr_planned_leaves_report.xml'],
    'data': [],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
