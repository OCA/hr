# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2011 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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

from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.osv import fields, orm
from openerp.tools.translate import _


class wage_increment(orm.Model):

    _name = 'hr.contract.wage.increment'
    _description = 'HR Contract Wage Increment'

    _columns = {
        'effective_date': fields.date(
            'Effective Date',
            required=True,
        ),
        'wage': fields.float(
            'Amount',
            digits=(16, 2)
        ),
        'contract_id': fields.many2one(
            'hr.contract',
            'Contract',
        ),
    }

    def _get_contract_id(self, cr, uid, context=None):

        if context is None:
            context = {}
        return context.get('active_id', False)

    _defaults = {'contract_id': _get_contract_id}

    _rec_name = 'effective_date'

    def action_wage_increment(self, cr, uid, ids, context=None):

        hr_obj = self.pool.get('hr.contract')

        # Copy the contract and adjust start/end dates and wage accordingly.
        #
        for wi in self.browse(cr, uid, ids, context=context):

            data = hr_obj.copy_data(
                cr, uid, wi.contract_id.id, context=context)
            data['name'] = data['name'] + \
                _(' - Wage Change ') + wi.effective_date
            data['wage'] = wi.wage
            data['date_start'] = wi.effective_date

            c_id = hr_obj.create(cr, uid, data, context=context)
            if c_id:
                effective_date = datetime.strptime(wi.effective_date,
                                                   '%Y-%m-%d').date()
                date_end = effective_date + relativedelta(days=1)
                vals = {
                    'date_end': date_end.stftime('%Y-%m-%d'),
                }
                hr_obj.write(cr, uid, wi.contract_id.id, vals, context=context)

        return {
            'type': 'ir.actions.act_window_close'
        }
