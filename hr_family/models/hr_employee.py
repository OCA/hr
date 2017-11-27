# -*- coding: utf-8 -*-

from openerp import _, api, models, fields
from openerp.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    fam_children_ids = fields.One2many(
        'hr.employee.children', 'employee_id', "Children")
    fam_father = fields.Char("Father's Name")
    fam_father_date_of_birth = fields.Date(
        "Date of Birth", oldname='fam_father_dob')
    fam_mother = fields.Char("Mother's Name")
    fam_mother_date_of_birth = fields.Date(
        "Date of Birth", oldname='fam_mother_dob')
    # you can't marry a company, corporations aren't people
    partner_spouse_id = fields.Many2one(
        'res.partner', string='Spouse', domain=[('is_company', '=', False)]
    )
    # TODO: use birthdate from partner_contact_birthdate instead.
    # (But if that, then also the children and parents to become partners)
    partner_spouse_date_of_birth = fields.Date("Spouse Date of Birth")
    marital_status_id = fields.Many2one(
        'hr.employee.marital.status', string='Marital status',
    )

    @api.constrains('partner_spouse_id')
    def _check_spouse_uniqueness(self):
        for this in self:
            if this.partner_spouse_id:
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
            'hr_family.res_partner_category_spouse'
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
            'hr_family.res_partner_category_spouse'
        ).id
        new_empl = super(HrEmployee, self).create(vals)
        # Add to the spouse partner "spouse" tag.
        new_empl.partner_spouse_id.with_context(
            auth_spouse_mod=True).write(
                {'category_id': [(4, spouse_tag_id)]}
            )
        return new_empl
