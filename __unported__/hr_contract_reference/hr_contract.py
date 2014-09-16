#-*- coding:utf-8 -*-
#
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
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

from osv import fields, osv


class hr_contract(osv.osv):

    _inherit = 'hr.contract'

    _columns = {
        'name': fields.char('Contract Reference', size=32, required=False, readonly=True),
    }

    def create(self, cr, uid, vals, context=None):

        cid = super(hr_contract, self).create(cr, uid, vals, context)
        if cid:
            ref = self.pool.get('ir.sequence').next_by_code(
                cr, uid, 'contract.ref', context=context)
            self.pool.get('hr.contract').write(
                cr, uid, cid, {'name': ref}, context=context)
        return cid
