# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from openerp.osv import fields, orm


class HrPayslipEmployees(orm.TransientModel):

    _inherit = 'hr.payslip.employees'

    def compute_sheet(self, cr, uid, ids, context=None):

        res = super(HrPayslipEmployees, self).compute_sheet(cr, uid, ids,
                                                            context=context)
        payslip_run = self.pool['hr.payslip.run'].browse(
                cr, uid, context['active_id'], context=context)
        move_date = payslip_run.move_date
        if move_date:
            period_obj = self.pool['account.period']
            period_ids = period_obj.find(cr, uid,
                                         dt=move_date,
                                         context=context)
            if period_ids:
                period_id = period_ids[0]
            else:
                period_id = False
            slip_ids = [slip.id for slip in payslip_run.slip_ids]
            self.pool['hr.payslip'].write(cr, uid, slip_ids,
                                          {'move_date': move_date,
                                           'period_id': period_id},
                                          context=context)
        return res
