# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
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

from openerp import fields, models, api


class Skill(models.Model):
    _name = 'hr.skill'
    _parent_store = True
    _order = 'parent_left'

    name = fields.Char('Name', required=True, translate=True)
    active = fields.Boolean('Active', default=True)
    parent_id = fields.Many2one('hr.skill', 'Parent', ondelete='cascade')
    parent_left = fields.Integer('Parent Left', index=True)
    parent_right = fields.Integer('Parent Right', index=True)
    child_ids = fields.One2many('hr.skill', 'parent_id', 'Children')
    employee_ids = fields.Many2many(
        'hr.employee',
        'skill_employee_rel',
        'skill_id',
        'employee_id',
        'Employee(s)')

    @api.multi
    def name_get(self):
        res = []
        for skill in self:
            names = []
            current = skill
            while current:
                names.append(current.name)
                current = current.parent_id
            res.append((skill.id, ' / '.join(reversed(names))))
        return res
