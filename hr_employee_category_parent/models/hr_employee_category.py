# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import _, api, exceptions, fields, models


class HrEmployeeCategory(models.Model):
    _inherit = 'hr.employee.category'

    parent_id = fields.Many2one('hr.employee.category', 'Parent category')

    @api.multi
    def name_get(self):
        return [
            (
                this.id,
                ' / '.join(
                    p.name for p in reversed(list(this._iter_parents(True)))
                ),
            )
            for this in self
        ]

    @api.multi
    def _iter_parents(self, include_self=False):
        self.ensure_one()
        if not include_self:
            self = self.parent_id
        while self:
            yield self
            self = self.parent_id

    @api.constrains('parent_id')
    def _constrain_parent_id(self):
        for this in self:
            for parent in this._iter_parents():
                if parent == this:
                    raise exceptions.ValidationError(
                        _('You can\'t create cyclic hierarchies'),
                    )
