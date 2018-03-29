# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2015 Salton Massally (<smassally@idtlabs.sl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import models, fields, api
from openerp.exceptions import Warning as UserWarning
from openerp.tools.safe_eval import safe_eval as eval


_default_text_rule_condition = '''
# Available variables:
#----------------------
# employee: hr.employee object
# contract: hr.contract object
# job: hr.job object
# date_ref: date object of the date being considered may or may not be today
#          to be safe use in place of datetime.date.today()
# Note: returned value have to be set in the variable 'result'

result = job.id in (1, 2, 3)'''


class HrHolidaysEvaluationRule(models.Model):
    _name = 'hr.holidays.evaluation.rule'

    name = fields.Char(required=True)
    sequence = fields.Integer(
        required=True,
        help='Use to arrange calculation sequence',
        index=True,
        default=5
    )
    ruleset_id = fields.Many2one(
        'hr.holidays.evaluation.ruleset',
        'Ruleset',
        required=True
    )
    active = fields.Boolean(default=True)
    condition_select = fields.Selection(
        [
            ('none', 'Always True'),
            ('range', 'Range'),
            ('python', 'Python Expression')
        ],
        "Condition Based on",
        required=True,
        default='none'
    )
    condition_range = fields.Char(
        'Range Based on',
        default='employee.length_of_service'
    )
    condition_range_min = fields.Float(
        'Minimum Range',
        help="The minimum amount, applied for this self."
    )
    condition_range_max = fields.Float(
        'Maximum Range',
        help="The maximum amount, applied for this rule."
    )
    condition_python = fields.Text(
        'Python Condition',
        help='Applied this rule for calculation if condition is true. '
             'You can specify condition like job.id in (1, 2, 3)',
        default=_default_text_rule_condition
    )
    amount = fields.Integer(
        'Amount of Days'
    )
    note = fields.Text('Description')

    @api.multi
    def satisfy_condition(self, localdict):
        """
        @return: returns True if the given rule match the condition for the
                 given employee. Return False otherwise.
        """
        self.ensure_one()
        if self.condition_select == 'none':
            return True
        elif self.condition_select == 'range':
            try:
                result = eval(self.condition_range, localdict)
                return (self.condition_range_min <= result
                        and result <= self.condition_range_max or False)
            except:
                raise UserWarning('Wrong range condition defined for '
                                  'allocation rule %s' % (self.name))
        else:  # python code
            try:
                eval(self.condition_python,
                     localdict, mode='exec', nocopy=True)
                return 'result' in localdict and localdict['result'] or False
            except:
                raise UserWarning('Wrong python condition defined for '
                                  'allocation rule %s' % (self.name))
