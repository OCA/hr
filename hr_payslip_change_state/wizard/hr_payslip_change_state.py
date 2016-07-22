# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Eficent (<http://www.eficent.com/>)
#              <contact@eficent.com>
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
from openerp.tools.translate import _
from openerp.exceptions import Warning
from openerp import netsvc

class HrPaySlipChangeState(orm.TransientModel):

    _name = "hr.payslip.change.state"
    _description = "Change state of a payslip"

    _columns = {
        'state': fields.selection([
            ('draft', 'Set to Draft'),
            ('verify', 'Compute Sheet'),
            ('done', 'Confirm'),
            ('cancel', 'Cancel Payslip'),
        ], 'Action',
            help='* When the payslip is created the status is \'Draft\'.\
            \n* If the payslip is under verification, the status is '
                 '\'Waiting\'. \
            \n* If the payslip is confirmed then status is set to \'Done\'.\
            \n* When user cancel payslip the status is \'Rejected\'.'),
    }

    def change_state_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        record_ids = context and context.get('active_ids', False)
        payslip_obj = self.pool.get('hr.payslip')
        new_state = data.get('state', False)
        records = payslip_obj.browse(cr, uid, record_ids, context=context)
        wf_service = netsvc.LocalService("workflow")

        for rec in records:
            if new_state == 'draft':
                if rec.state == 'cancel':
                    wf_service.trg_validate(uid, 'hr.payslip', rec.id,
                                            'draft', cr)
                else:
                    raise Warning(_("Only rejected payslips can be reset to "
                                    "draft, the payslip %s is in "
                                    "%s state" % (rec.name, rec.state)))
            elif new_state == 'verify':
                if rec.state == 'draft':
                    payslip_obj.compute_sheet(cr, uid, [rec.id],
                                              context=context)
                else:
                    raise Warning(_("Only draft payslips can be verified,"
                                    "the payslip %s is in "
                                    "%s state" % (rec.name, rec.state)))
            elif new_state == 'done':
                if rec.state in ('verify','draft'):
                    wf_service.trg_validate(uid, 'hr.payslip', rec.id,
                                            'hr_verify_sheet', cr)
                else:
                    raise Warning(_("Only payslips in states verify or draft "
                                    "can be confirmed, the payslip %s is in "
                                    "%s state" % (rec.name, rec.state)))
            elif new_state == 'cancel':
                if rec.state != 'cancel':
                    wf_service.trg_validate(uid, 'hr.payslip', rec.id,
                                            'cancel_sheet', cr)
                else:
                    raise Warning(_("The payslip %s is already canceled "
                                    "please deselect it" % rec.name))

        return {
            'domain': "[('id','in', ["+','.join(map(str, record_ids))+"])]",
            'name': _('Payslips'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.payslip',
            'view_id': False,
            'context': False,
            'type': 'ir.actions.act_window'
        }
