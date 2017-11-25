# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import _, api, models
from openerp.exceptions import Warning as UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def spouse_check(self, vals):
        spouse_tag_id = self.env.ref(
            'hr_employee_spouse.res_partner_category_spouse'
        ).id
        new_categories = [
            x.values()[0] for x in self.resolve_2many_commands(
                'category_id', vals['category_id'], ['id'])]
        # check if calling from create
        if not self.id and spouse_tag_id in new_categories:
            raise UserError(_(
                'Error: you cannot create a partner with spouse tag'
                'create the partner and then specify spouse in the'
                'employeer form'))
        # removing from existing record
        if (spouse_tag_id in self.category_id.ids and
                spouse_tag_id not in new_categories):
            spouse_rec = self.env['hr.employee'].search(
                [('partner_spouse_id', '=', self.id)]
            )
            raise UserError(_(
                'Error: you cannot remove the spouse tag via form.'
                ' {0} is the spouse of {1}, you must delete spouse'
                ' relationship be removing \'spouse\' from {1}'.format(
                    self.name, spouse_rec.name
                )
            ))
        # Adding from partner where no spouse was
        if (spouse_tag_id not in self.category_id.ids and
                spouse_tag_id in new_categories):
            raise UserError(_(
                'Error: you cannot add the spouse tag via form. specify '
                ' spouse from employee form'
                ))
        return False

    @api.multi
    def write(self, vals):
        for this in self:
            auth_spouse_mod = self.env.context.get('auth_spouse_mod')
            if 'category_id' in vals and not auth_spouse_mod:
                this.spouse_check(vals)
        return super(ResPartner, self).write(vals=vals)

    @api.model
    def create(self, vals):
        auth_spouse_mod = self.env.context.get('auth_spouse_mod')
        if 'category_id' in vals and not auth_spouse_mod:
            self.spouse_check(vals)
        return super(ResPartner, self).create(vals)
