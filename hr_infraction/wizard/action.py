#-*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
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
##############################################################################

from openerp import netsvc
from openerp.osv import fields, osv

from openerp.addons.hr_infraction.hr_infraction import ACTION_TYPE_SELECTION

class action_wizard(osv.TransientModel):
    
    _name = 'hr.infraction.action.wizard'
    _description = 'Choice of Actions for Infraction'
    
    _columns = {
        'action_type': fields.selection(ACTION_TYPE_SELECTION, 'Action', required=True),
        'memo': fields.text('Notes'),
        'new_job_id': fields.many2one('hr.job', 'New Job'),
        'xfer_effective_date': fields.date('Effective Date'),
        'effective_date': fields.date('Effective Date'),
    }
    
    def create_action(self, cr, uid, ids, context=None):
        
        if context == None: context = {}
        infraction_id = context.get('active_id', False)
        if not infraction_id:
            return False
        data = self.read(cr, uid, ids[0], context=context)
        
        vals = {
            'infraction_id': infraction_id,
            'type': data['action_type'],
            'memo': data.get('memo', False),
        }
        action_id = self.pool.get('hr.infraction.action').create(cr, uid, vals, context=context)
        
        # Update state of infraction, if not already done so
        #
        infraction_obj = self.pool.get('hr.infraction')
        infraction_data = infraction_obj.read(cr, uid, infraction_id, ['employee_id', 'state'],
                                              context=context)
        if infraction_data['state'] == 'confirm':
            netsvc.LocalService('workflow').trg_validate(uid, 'hr.infraction', infraction_id,
                                                         'signal_action', cr)
        
        infraa_obj = self.pool.get('hr.infraction.action')
        imd_obj = self.pool.get('ir.model.data')
        iaa_obj = self.pool.get('ir.actions.act_window')

        # If the action is a warning create the appropriate record, reference it from the action,
        # and pull it up in the view (in case the user needs to make any changes.
        #
        if data['action_type'] in ['warning_verbal', 'warning_letter']:
            vals = {
                'name': (data['action_type'] == 'warning_verbal' and 'Verbal' or 'Written') + ' Warning',
                'type': data['action_type'] == 'warning_verbal' and 'verbal' or 'written',
                'action_id': action_id,
            }
            warning_id = self.pool.get('hr.infraction.warning').create(cr, uid, vals, context=context)
            infraa_obj.write(cr, uid, action_id, {'warning_id': warning_id}, context=context)
            
            res_model, res_id = imd_obj.get_object_reference(cr, uid, 'hr_infraction',
                                                             'open_hr_infraction_warning')
            dict_act_window = iaa_obj.read(cr, uid, res_id, [])
            dict_act_window['view_mode'] = 'form,tree'
            dict_act_window['domain'] = [('id', '=', warning_id)]
            return dict_act_window
        
        # If the action is a departmental transfer create the appropriate record, reference it from
        # the action, and pull it up in the view (in case the user needs to make any changes.
        #
        elif data['action_type'] == 'transfer':
            xfer_obj = self.pool.get('hr.department.transfer')
            ee = self.pool.get('hr.employee').browse(cr, uid, infraction_data['employee_id'][0],
                                                     context=context)
            _tmp = xfer_obj.onchange_employee(cr, uid, None, ee.id, context=context)
            vals = {
                'employee_id': ee.id,
                'src_id': _tmp['value']['src_id'],
                'dst_id': data['new_job_id'][0],
                'src_contract_id': _tmp['value']['src_contract_id'],
                'date': data['xfer_effective_date'],
            }
            xfer_id = xfer_obj.create(cr, uid, vals, context=context)
            infraa_obj.write(cr, uid, action_id, {'transfer_id': xfer_id}, context=context)
            
            res_model, res_id = imd_obj.get_object_reference(cr, uid, 'hr_transfer',
                                                             'open_hr_department_transfer')
            dict_act_window = iaa_obj.read(cr, uid, res_id, [])
            dict_act_window['view_mode'] = 'form,tree'
            dict_act_window['domain'] = [('id', '=', xfer_id)]
            return dict_act_window
        
        # The action is dismissal. Begin the termination process.
        #
        elif data['action_type'] == 'dismissal':
            term_obj = self.pool.get('hr.employee.termination')
            wkf = netsvc.LocalService('workflow')
            ee = self.pool.get('hr.employee').browse(cr, uid, infraction_data['employee_id'][0],
                                                     context=context)
            
            # We must create the employment termination object before we set
            # the contract state to 'done'. 
            res_model, res_id = imd_obj.get_object_reference(cr, uid, 'hr_infraction', 'term_dismissal')
            vals = {
                'employee_id': ee.id,
                'name': data['effective_date'],
                'reason_id': res_id,
            }
            term_id = term_obj.create(cr, uid, vals, context=context)
            infraa_obj.write(cr, uid, action_id, {'termination_id': term_id}, context=context)
            
            # End any open contracts
            for contract in ee.contract_ids:
                if contract.state not in ['done']:
                    wkf.trg_validate(uid, 'hr.contract', contract.id, 'signal_pending_done', cr)
            
            # Set employee state to pending deactivation
            wkf.trg_validate(uid, 'hr.employee', ee.id, 'signal_pending_inactive', cr)

            # Trigger confirmation of termination record
            wkf.trg_validate(uid, 'hr.employee.termination', term_id, 'signal_confirmed', cr)
            
            res_model, res_id = imd_obj.get_object_reference(cr, uid, 'hr_employee_state',
                                                             'open_hr_employee_termination')
            dict_act_window = iaa_obj.read(cr, uid, res_id, [])
            dict_act_window['domain'] = [('id', '=', term_id)]
            return dict_act_window
        
        return True
