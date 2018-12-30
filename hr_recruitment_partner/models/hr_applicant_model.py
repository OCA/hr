##############################################################################
#
#    Copyright (C) 2015 Daniel Reis
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

from odoo import api, models, fields


class Applicant(models.Model):
    _inherit = 'hr.applicant'

    partner_id = fields.Many2one(
        delegate=True, ondelete='restrict')

    # Redefined fields, now stored in Partner only
    partner_name = fields.Char(related='partner_id.name')
    partner_mobile = fields.Char(related='partner_id.mobile')
    partner_phone = fields.Char(related='partner_id.phone')
    image = fields.Binary(related='partner_id.image')

    @api.model
    def create(self, vals):
        if not vals.get('partner_id', False):
            vals['partner_id'] = (
                self.env['res.partner']
                .create(
                    {
                        'is_company': False,
                        'name': vals.get('partner_name', False),
                        'email': vals.get('partner_email', False),
                        'phone': vals.get('phone', False),
                        'mobile': vals.get('mobile', False),
                        'image': vals.get('image', False),
                    }
                )
                .id
            )

        return super(Applicant, self).create(vals)
