# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
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
#

{
    "name": "HR Wage Increment",
    "version": "1.0",
    "category": "Generic Modules/Human Resources",
    "description": """
Wage Increment Handling
=======================

    This module provides a way to handle wage increments that automatically
    creates a new contract for the rest of the duration of the employee's
    current contract with the new amount.
    """,
    "author": "Michael Telahun Makonnen <mmakonnen@gmail.com,Odoo Community Association (OCA)",
    "website": "http://www.openerp.com",
    "depends": [
        "hr_contract_state",
        "hr_payroll_period",
        "hr_security",
    ],
    "external_dependencies": {
        'python': ['dateutil'],
    },
    "data": [
        'security/ir.model.access.csv',
        'wizard/wage_adjustment_by_employees.xml',
        'wage_adjustment_run_workflow.xml',
        'wage_increment_view.xml',
        'wage_increment_workflow.xml',
    ],
    'installable': True,
}
