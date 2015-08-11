# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2011 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp import api, models, fields


class hr_employee(models.Model):

    _name = 'hr.employee'
    _inherit = 'hr.employee'

    ec_name = fields.Char('Name', size=256)
    ec_relationship = fields.Char('Relationship', size=64)
    ec_tel1 = fields.Char('Primary Phone No.', size=32)
    ec_tel2 = fields.Char('Secondary Phone No.', size=32)
    ec_woreda = fields.Char('Subcity/Woreda', size=32)
    ec_kebele = fields.Char('Kebele', size=8)
    ec_houseno = fields.Char('House No.', size=8)
    ec_address = fields.Char('Address 2', size=256)
    ec_country_id = fields.Many2one('res.country', 'Country')
    ec_state_id = fields.Many2one('res.country.state', 'State', domain="[('country_id','=',country_id)]")

    @api.multi
    def _get_country(self):
        cid = self.pool.get('res.country').search(self.env.cr, self.env.user.id, [('code', '=', 'ET')])
        return cid[0]

    _defaults = {
        'ec_country_id': _get_country,
    }
