# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
#               <jordi.ballester@eficent.com>
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
from openerp.osv import fields, osv, orm


class HrPayslip(orm.Model):

    _inherit = 'hr.payslip'

    _columns = {
        'move_date': fields.date(string='Force move date',
                                 required=False),
    }

    def onchange_move_date(self, cr, uid, ids, move_date, context=None):
        res = {'value': {}}
        period_obj = self.pool['account.period']
        if move_date:
            period_ids = period_obj.find(cr, uid, dt=move_date,
                                         context=context)
            if period_ids:
                res['value']['period_id'] = period_ids[0]
        return res

    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context = {}
        move_obj = self.pool['account.move']
        move_line_obj = self.pool['account.move.line']

        res = super(HrPayslip, self).write(cr, uid, ids, vals, context=context)
        if 'move_id' in vals and vals['move_id']:
            for slip in self.browse(cr, uid, ids, context=context):
                if slip.move_date:
                    move_obj.write(cr, uid, [slip.move_id.id],
                                   {'date': slip.move_date}, context=context)
                    for move_line in slip.move_id.line_id:
                        move_line_obj.write(cr, uid, [move_line.id],
                                            {'date': slip.move_date},
                                            context=context)
                else:
                    self.write(cr, uid, [slip.id],
                               {'move_date': slip.move_id.date},
                               context=context)
        return res


class HrPayslipRun(orm.Model):

    _inherit = 'hr.payslip.run'

    _columns = {
        'move_date': fields.date(string='Force move date',
                                 required=False),
    }
