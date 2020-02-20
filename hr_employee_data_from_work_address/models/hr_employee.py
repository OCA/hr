# -*- coding: utf-8 -*-
# Copyright 2015 Therp BV <http://therp.nl>
from openerp import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    work_phone = fields.Char(related=['address_id', 'phone'], store=True)
    work_email = fields.Char(related=['address_id', 'email'], store=True)
    mobile_phone = fields.Char(related=['address_id', 'mobile'], store=True)
    image = fields.Binary(related=['address_id', 'image'], store=False)
    image_medium = fields.Binary(
        related=['address_id', 'image_medium'], store=False)
    image_small = fields.Binary(
        related=['address_id', 'image_small'], store=False)

    def _onchange_company(self):
        """defuse entirely"""
        pass

    def _onchange_address(self):
        """defuse entirely"""
        pass

    def _onchange_user(self):
        """defuse entirely"""
        pass

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
            old_partner.unlink()

    @api.multi
    def write(self, values):
        result = super(HrEmployee, self).write(values)
        self._reassign_user_id_partner(values)
        return result

    @api.model
    def create(self, values):
        result = super(HrEmployee, self).create(values)
        result._reassign_user_id_partner(values)
        return result

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        result = super(HrEmployee, self).read(fields=fields, load=load)
        return result
