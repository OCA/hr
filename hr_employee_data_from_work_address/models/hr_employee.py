# -*- coding: utf-8 -*-
# Copyright 2015 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import _, api, fields, models
from openerp.exceptions import AccessError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    work_phone = fields.Char(related=['address_id', 'phone'], store=False)
    work_email = fields.Char(related=['address_id', 'email'], store=False)
    mobile_phone = fields.Char(related=['address_id', 'mobile'], store=False)
    image = fields.Binary(related=['address_id', 'image'], store=False)
    image_medium = fields.Binary(
        related=['address_id', 'image_medium'], store=False)
    image_small = fields.Binary(
        related=['address_id', 'image_small'], store=False)

    @api.multi
    def onchange_company(self, company):
        result = super(HrEmployee, self).onchange_company(company)
        result['value'].pop('address_id')
        return result

    @api.multi
    def onchange_address_id(self, address):
        result = super(HrEmployee, self).onchange_address_id(address)
        for field in ['work_phone', 'mobile_phone']:
            if field in result['value']:
                result['value'].pop(field)
        return result

    def _register_hook(self, cr):
        # we need to reset the store parameter
        # further, making a normal field related doesn't reset columns
        for field in [
            'work_phone', 'work_email', 'mobile_phone', 'image',
            'image_medium', 'image_small',
        ]:
            if field in self._columns:
                self._columns[field].store = False
                self._fields[field].column = self._columns[field]
            self._fields[field].store = False
            self.pool._store_function[self._name] = [
                spec
                for spec in self.pool._store_function[self._name]
                if spec[1] != field
            ]

        return super(HrEmployee, self)._register_hook(cr)

    @api.multi
    def _reassign_user_id_partner(self, values):
        '''if we assigned a user, replace its partner_id by our work address'''
        if 'user_id' not in values:
            return
        for this in self:
            if not this.address_id:
                this.write({'address_id': this.user_id.partner_id.id})
                continue
            # take some precautions
            if this.user_id.partner_id == this.address_id:
                continue
            # don't drop the partner if we recycle users
            if self.search(
                    [
                        ('id', '!=', this.id),
                        ('user_id', '=', this.user_id.id),
                    ]):
                continue
            old_partner = this.user_id.partner_id
            this.user_id.write({'partner_id': this.address_id.id})
            try:
                old_partner.unlink()
            except AccessError:
                old_partner.message_post(_(
                    'Replaced by partner id {}. Deactivated, because deleting '
                    'gave AccessError.'.format(this.address_id.id)))
                old_partner.write({'active': False})

    @api.multi
    def write(self, values):
        result = super(HrEmployee, self).write(values)
        self._reassign_user_id_partner(values)
        return result

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, values):
        result = super(HrEmployee, self).create(values)
        result._reassign_user_id_partner(values)
        return result
