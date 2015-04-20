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

    address_id = fields.Many2one(required=True)
    work_phone = fields.Char(related=['address_id', 'phone'])
    work_email = fields.Char(related=['address_id', 'email'])
    mobile_phone = fields.Char(related=['address_id', 'mobile'])

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
