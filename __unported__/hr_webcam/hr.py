# -*- coding:utf-8 -*-

from openerp.osv import orm


class hr_employee(orm.Model):

    _name = 'hr.employee'
    _inherit = 'hr.employee'

    def action_take_picture(self, cr, uid, ids, context=None):
        data_pool = self.pool.get('ir.model.data')
        client_pool = self.pool.get('ir.actions.client')
        res_model, res_id = data_pool.get_object_reference(
            cr, uid, 'hr_webcam', 'action_take_photo',
        )
        dict_act_window = client_pool.read(cr, uid, res_id, [])
        if not dict_act_window.get('params', False):
            dict_act_window.update({'params': {}})
        dict_act_window['params'].update({
            'employee_id': len(ids) and ids[0] or False,
        })
        return dict_act_window
