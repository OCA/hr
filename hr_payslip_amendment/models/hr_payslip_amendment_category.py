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
from openerp.exceptions import ValidationError, Warning as UserWarning


class HrPayslipAmendmentCategory(models.Model):
    _name = 'hr.payslip.amendment.category'

    name = fields.Char(
        'Name',
        size=128,
        required=True
    )
    type = fields.Selection(
        [('add', 'Addition'), ('subtract', 'Deduction')],
        required=True,
        default='add'
    )
    code = fields.Char(
        'Code',
        size=10,
        required=True
    )
    struct_id = fields.Many2one(
        'hr.payroll.structure',
        'Payroll Structure',
        required=True,
        help="Salary structure to add amendment category rule to"
    )
    in_report = fields.Boolean('Show in Reports')
    rule_id = fields.Many2one(
        'hr.salary.rule',
        'Salary Rule',
        readonly=True
    )
    input_rule_id = fields.Many2one(
        'hr.rule.input',
        'Input Rule',
        readonly=True,
    )
    active = fields.Boolean(
        'Active',
        default=True
    )
    note = fields.Text('Memo')

    _sql_constraints = [
        ('category_code_uniq', 'unique(code)', 'Another amendment category '
         'exists with this code'),
    ]

    @api.constrains('code')
    @api.one
    def _check_code(self):
        # let's ensure that we do not already have salary rule with this code
        domain = []
        domain.append(('code', '=', self.code))
        if self.rule_id:
            domain.append(('id', 'not in', (self.rule_id.id,)))
        if self.env['hr.salary.rule'].search_count(domain) > 0:
            raise ValidationError('Amendment category code conflicts with a '
                                  'salary rule code.')

        # let's ensure that we do not already have input rule with this code
        domain = []
        domain.append(('code', '=', self.code))
        if self.input_rule_id:
            domain.append(('id', 'not in', (self.input_rule_id.id,)))
        if self.env['hr.rule.input'].search_count(domain) > 0:
            raise ValidationError('Amendment category code conflicts with an '
                                  'input rule code.')
        return True

    @api.model
    def create(self, vals):
        res = super(HrPayslipAmendmentCategory, self).create(vals)
        rule_obj = self.env['hr.salary.rule']
        struct_obj = self.env['hr.payroll.structure']
        input_rule_obj = self.env['hr.rule.input']

        update = {}
        # creating payroll fields
        note = vals.get('note', False)
        if note:
            note += ' - Auto created via payroll amendments'
        else:
            note = 'Auto created via payroll amendments'

        # let's create a payroll rule for category
        if res.type == 'add':
            rule_category = self.env.ref('hr_payroll.ALW')
            sequence = 80
        else:
            rule_category = self.env.ref('hr_payroll.DED')
            sequence = 102
        rule_data = {
            'code': vals['code'].upper(),
            'name': vals['name'],
            'category_id': rule_category.id,
            'condition_select': 'python',
            'amount_select': 'code',
            'amount_python_compute':
                'result = inputs.%s.amount' % (vals['code'].upper()),
            'sequence': sequence,
            'note': note,
            'condition_python':
                'result = inputs.%s and inputs.%s.amount'
                % (vals['code'].upper(), vals['code'].upper()),
        }
        rule = rule_obj.create(rule_data)
        update['rule_id'] = rule.id

        # let's create input rule for this category
        input_rule_data = {
            'code': vals['code'].upper(),
            'name': vals['name'],
            'input_id': rule.id
        }
        input_rule = input_rule_obj.create(input_rule_data)
        update['input_rule_id'] = input_rule.id

        # let's assign to salary structure
        struct = struct_obj.browse(vals['struct_id'])
        struct.write({'rule_ids': [(4, rule.id), ], })

        # lets update the category
        res.write(update)
        return res

    @api.multi
    def write(self, data):
        for category in self:
            if 'code' in data:
                raise UserWarning('Sorry, you can\'t edit the code once it '
                                  'has been created')
            # let's handle inactivation
            if 'active' in data:
                category.rule_id.active = data['active']

        return super(HrPayslipAmendmentCategory, self).write(data)

    @api.multi
    def copy(self):
        raise UserWarning('Salary category does not support duplication!')

    @api.multi
    def unlink(self):
        for category in self:
            category.rule_id.unlink()
            category.input_rule_id.unlink()
        return super(HrPayslipAmendmentCategory, self).unlink()
