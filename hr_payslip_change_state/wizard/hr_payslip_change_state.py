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
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.exceptions import Warning

class hr_payslip_change_state(osv.osv_memory):

    _name = "hr.payslip.change.state"
    _description = "Change state of a payslip"

    _columns = {
        'state': fields.selection([
            ('draft', 'Draft'),
            ('verify', 'Waiting'),
            ('done', 'Done'),
            ('cancel', 'Rejected'),
        ], 'Status',
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

        for rec in records:
            if new_state == 'draft' and rec.state != 'cancel':
                raise Warning(_("Only rejected payslips can be reset to "
                                "draft, the payslip %s is in "
                                "%s state" % (rec.name, rec.state)))
            elif new_state == 'verify' and rec.state != 'draft':
                raise Warning(_("Only draft payslips can be verified,"
                                "the payslip %s is in "
                                "%s state" % (rec.name, rec.state)))
            elif new_state == 'done' and rec.state not in ('verify','draft'):
                raise Warning(_("Only payslips in states verify or draft "
                                "can be confirmed, the payslip %s is in "
                                "%s state" % (rec.name, rec.state)))
            elif new_state == 'cancel' and rec.state == 'cancel':
                raise Warning(_("The payslip %s is already canceled "
                                "please deselect it" % rec.name))

        for rec in records:
            if new_state == 'draft' and rec.state == 'cancel':
                payslip_obj.draft_sheet(cr, uid, [rec.id],
                                                  context=context)
            elif new_state == 'verify' and rec.state == 'draft':
                payslip_obj.hr_verify_sheet(cr, uid, [rec.id],
                                                    context=context)
            elif new_state == 'done' and rec.state in ('verify','draft'):
                payslip_obj.process_sheet(cr, uid, [rec.id],
                                       context=context)
            elif new_state == 'cancel' and rec.state != 'cancel':
                payslip_obj.cancel_sheet(cr, uid, [rec.id],
                                                    context=context)
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
