# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Savoir-faire Linux. All Rights Reserved.
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
    'name': 'Employee Benefit On Job',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'author': "Savoir-faire Linux, Odoo Community Association (OCA)",
    'website': 'https://www.savoirfairelinux.com',
    'description': """
Employee Benefit On Job
=======================
Add the possibility to put employee benefits on the job.
Add employee benefits computed per hour for each job the employee works on.
Each worked days record related to a job will trigger benefits.
    """,
    'depends': [
        'hr_contract_multi_jobs',
        'hr_employee_benefit',
        'hr_worked_days_activity',
        'hr_worked_days_hourly_rate',
    ],
    'data': [
        'view/hr_job.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
}
