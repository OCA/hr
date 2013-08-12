from openerp.osv import fields, osv

class hr_employee(osv.Model):
    
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    
    def action_take_picture(self, cr, uid, ids, context=None):
        
        if context == None:
            context = {}
        
        res_model, res_id = self.pool.get('ir.model.data').get_object_reference(cr, uid,
                                                                                'hr_webcam',
                                                                                'action_take_photo')
        dict_act_window = self.pool.get('ir.actions.client').read(cr, uid, res_id, [])
        if not dict_act_window.get('params', False):
            dict_act_window.update({'params': {}})
        dict_act_window['params'].update({'employee_id': len(ids) and ids[0] or False})
        return dict_act_window