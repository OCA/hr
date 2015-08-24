# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
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

from openerp import models, fields, api, _


class HrDepartment(models.Model):
    _inherit = 'hr.department'
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'sequence, name'
    _order = 'sequence, name'

    code = fields.Char()
    sequence = fields.Integer(string='Sequence', index=True,
                              help="Gives the sequence order when displaying "
                              "a list of departments.")
    parent_id = fields.Many2one(ondelete='restrict')
    parent_left = fields.Integer(string='Left Parent', index=True)
    parent_right = fields.Integer(string='Right Parent', index=True)
    child_ids = fields.One2many(comodel_name='hr.department',
                                inverse_name='parent_id',
                                string='Children Departments')
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code, company_id)',
         _('The code for the department must be unique per company!')),
    ]

    @api.one
    def copy(self, default=None):
        default = dict(default or {})
        if self.code and not default.get('code'):
            default['code'] = _("%s (copy)") % self.code
        return super(HrDepartment, self).copy(default)

    @api.one
    def name_get(self):
        name = self.name
        if self.code:
            name = '[%s] %s' % (self.code, name)
        return (self.id, name)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = list(args or [])
        if name:
            search_name = name
            if operator != '=':
                search_name = '%s%%' % name
            departments = self.search([('code', operator, search_name)] + args,
                                      limit=limit)
            if departments.ids:
                return departments.name_get()
        return super(HrDepartment, self)\
            .name_search(name=name, args=args, operator=operator, limit=limit)
