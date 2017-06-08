# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by
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

from openerp.osv import orm


class hr_salary_rule(orm.Model):
    _defaults = {
        'amount_python_compute': '''
# Available variables:
# --------------------
# payslip: object containing the payslips
# rules: object containing the rules code (previously computed)
# categories: object containing the computed salary rule categories \
(sum of amount of all rules belonging to that category).

# Available in Payslip:
# ---------------------
# worked_days: object containing the computed worked days
# inputs: object containing the computed inputs
# employee: hr.employee object
# contract: hr.contract object

# Available in Employer Contribution:
# ------------------------------------
# contribution: object containing the employer contribution

# Note: returned value have to be set in the variable 'result'

result = rules.NET > categories.NET * 0.10''',

        'condition_python': '''
# Available variables:
# --------------------
# payslip: object containing the payslips
# rules: object containing the rules code (previously computed)
# categories: object containing the computed salary rule categories \
(sum of amount of all rules belonging to that category).

# Available in Payslip:
# ---------------------
# worked_days: object containing the computed worked days
# inputs: object containing the computed inputs
# employee: hr.employee object
# contract: hr.contract object

# Available in Employer Contribution:
# ------------------------------------
# contribution: object containing the employer contribution

# Note: returned value have to be set in the variable 'result'

result = rules.NET > categories.NET * 0.10''',
    }
