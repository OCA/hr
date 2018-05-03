# -*- coding: utf-8 -*-
# © 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# © 2018 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree
from openerp import fields, models, api, SUPERUSER_ID


class HrSkill(models.Model):
    _name = 'hr.skill'
    _parent_store = True
    _parent_order = 'name'
    _order = 'parent_left'

    state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    ], default=lambda self: self._default_state())
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
    dummy_display_name = fields.Char(
        string='Display name',
        search='_search_dummy_display_name',
        compute=lambda self: None)

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError(
                'Error! You cannot create recursive categories.')

    @api.model
    def _search_dummy_display_name(self, operator, value):
        """ Search skills on name and parent name(s) in tree views
            (add the 'dummy_display_name' field in your search views)"""
        results = self.name_search(value, operator=operator)
        ids = [_id[0] for _id in results]
        return [('id', 'in', ids)]

    @api.multi
    def name_get(self):
        """ Display search results including categories """
        res = []
        for skill in self:
            names = []
            current = skill
            while current:
                names.append(current.name)
                current = current.parent_id
            res.append((skill.id, ' / '.join(reversed(names))))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """ Search skills on name and parent name(s) for many2one fields """
        args = args or []
        args = [
            arg for arg in args
            if not (arg[0] == 'child_ids' and not arg[2])
        ]
        if name:
            args = [('name', operator, name)] + args
        locs = self.search(args, limit=limit)
        domain_with_children = [('id', 'child_of', locs.ids)]
        locs = self.search(domain_with_children, limit=limit)
        return locs.name_get()

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        result = super(HrSkill, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu
        )

        if view_type == 'search':
            arch = etree.fromstring(result['arch'])
            for skill in self.env['hr.skill'].search([
                ('child_ids', '!=', False),
                ('parent_id', '=', False)
            ]):
                _domain = \
                    "[" + \
                    "('id', 'child_of', %d)" % skill.id + \
                    ", " + \
                    "('child_ids', '=', False)" + \
                    "]"
                etree.SubElement(arch, 'filter', {
                    'string': skill.name,
                    'domain': _domain,
                })
            result['arch'] = etree.tostring(arch)
        return result

    @api.model
    def _default_state(self):
        if self.env.ref('base.group_hr_manager') in self.env.user.groups_id \
                or self.env.user.id == SUPERUSER_ID:
            state = 'approved'
        else:
            state = 'pending'
        return state

    @api.multi
    def action_approve(self):
        return self.write({
            'state': 'approved',
        })

    @api.multi
    def action_reject(self):
        return self.unlink()

    @api.model
    def create(self, vals):
        ret = super(HrSkill, self).create(vals)
        self._parent_store_compute()
        return ret

    @api.multi
    def write(self, vals):
        ret = super(HrSkill, self).write(vals)
        if 'name' in vals or 'parent_id' in vals:
            self._parent_store_compute()
        return ret
