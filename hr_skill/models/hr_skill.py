# -*- coding: utf-8 -*-
# Copyright 2013 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
