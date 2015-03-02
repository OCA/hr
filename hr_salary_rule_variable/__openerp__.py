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
    'name': 'Salary Rule Variables',
    'category': 'Localization',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'description': """
Salary Rule Variables
=====================
Salary rule variables are amounts or python expressions that change over
the years. This module allows to compute these variables and reference
them from salary rules.

The purpose of this module is to be able to adapt a complexe salary structures
(e.g. the canadian income tax structure) from one year to another without
going each time through the whole testing procedure.

Numbers change but the whole logic stays the same.

How to use it
-------------
In the python script of a salary rule, you may call it via the payslip
browsable object:
    variable = payslip.get_rule_variable(rule_id, payslip.date_from)

rule_id always refer to the current rule.

If you need more than one variable for a salary rule, use a python dict.

Contributors
------------
* David Dufresne <david.dufresne@savoirfairelinux.com>
* Pierre Lamarche <pierre.lamarche@savoirfairelinux.com>
""",
    'author': "Savoir-faire Linux,Odoo Community Association (OCA)",
    'website': 'https://www.savoirfairelinux.com',
    'depends': [
        'hr_payroll',
    ],
    'data': [
        'security/ir.model.access.csv',
        'hr_salary_rule_variable_view.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
}
