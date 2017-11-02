# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models, _
from openerp.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # you can't marry a company, corporations aren't people
    partner_spouse_id = fields.Many2one(
        'res.partner', string='Spouse', domain=[('is_company', '=', False)]
    )

    @api.constrains('partner_spouse_id')
    def _check_spouse_uniqueness(self):
        for this in self:
            spouse = self.search(
                [('partner_spouse_id', '=', this.partner_spouse_id.id),
                 ('id', '!=', this.id)],
                limit=1
            )
            if spouse:
                raise ValidationError(_(
                    'Error: {0} cannot have this spouse, because'
                    ' already the spouse of {1}'.format(
                        this.name, spouse.name
                    )
                ))

    @api.multi
    def write(self, vals):
        # note the write super needs to be done before so that if constrainst
        # fail we won't change tags. Tests revealed that those writes below on
        # partner will not be rolledback by the validation error in constraint
        old_partners = self.mapped('partner_spouse_id')
        res = super(HrEmployee, self).write(vals)
        spouse_tag_id = self.env.ref(
            'hr_employee_spouse.res_partner_category_spouse'
        ).id
        if 'partner_spouse_id' in vals:
            # delete "spouse" tag from old partners
            old_partners.with_context(
                auth_spouse_mod=True).write(
                    {'category_id': [(3, spouse_tag_id)]}
                )
            # Add to the spouse partner "spouse" tag.
            self.mapped('partner_spouse_id').with_context(
                auth_spouse_mod=True).write(
                    {'category_id': [(4, spouse_tag_id)]}
                )
        return res

    @api.model
    def create(self, vals):
        spouse_tag_id = self.env.ref(
            'hr_employee_spouse.res_partner_category_spouse'
        ).id
        new_empl = super(HrEmployee, self).create(vals)
        # Add to the spouse partner "spouse" tag.
        new_empl.partner_spouse_id.with_context(
            auth_spouse_mod=True).write(
                {'category_id': [(4, spouse_tag_id)]}
            )
        return new_empl
