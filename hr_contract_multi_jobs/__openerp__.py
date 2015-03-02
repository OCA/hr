# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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
    'name': 'Contract Multi Jobs',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'description': """
Contract Multi Jobs
===================
In some companies, one employee may have more than one job position with a
different hourly rate based wage.

An example is a construction worker who makes different types of jobs
for the same company like bricklaying, electricity, carpentry.

Also in restaurants, a waiter can also work as a barman.

This module enables multiple job positions for one contract

Contributors
------------
* David Dufresne <david.dufresne@savoirfairelinux.com>
* Pierre Lamarche <pierre.lamarche@savoirfairelinux.com>
""",
    'author': "Savoir-faire Linux,Odoo Community Association (OCA)",
    'website': 'https://www.savoirfairelinux.com/',
    'depends': [
        'hr_contract'
    ],
    'data': [
        'security/ir.model.access.csv',
        'hr_contract_view.xml',
    ],
    'test': ['test/hr_contract_job_test.yml'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
