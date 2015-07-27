# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    work_phone = fields.Char(related=['address_id', 'phone'])
    work_email = fields.Char(related=['address_id', 'email'])
    mobile_phone = fields.Char(related=['address_id', 'mobile'])
    image = fields.Binary(related=['address_id', 'image'])
    image_medium = fields.Binary(related=['address_id', 'image_medium'])
    image_small = fields.Binary(related=['address_id', 'image_small'])

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
        for field in ['work_phone', 'work_email', 'mobile_phone', 'image',
                      'image_medium', 'image_small']:
            if field in self._columns:
                self._columns.pop(field)
            if field in self._all_columns:
                self._all_columns.pop(field)
            self._fields[field].store = False
            self._fields[field].column = None
        return super(HrEmployee, self)._register_hook(cr)

    @api.multi
    def _reassign_user_id_partner(self, values):
        '''if we assigned a user, replace its partner_id by our work address'''
        if 'user_id' not in values:
            return
        for this in self:
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
    @api.returns('self', lambda value: value.id)
    def create(self, values):
        result = super(HrEmployee, self).create(values)
        result._reassign_user_id_partner(values)
        return result
