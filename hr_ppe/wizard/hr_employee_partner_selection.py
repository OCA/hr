# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class HrEmployeePartnerSelection(models.TransientModel):
    _name = 'hr.employee.partner.selection'

    employee_id = fields.Many2one(
        comodel_name='hr.employee', string='Employee', required=True)
    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Home Address')

    @api.model
    def default_get(self, fields_list):
        res = super(HrEmployeePartnerSelection, self).default_get(fields_list)
        active_id = self.env.context.get('active_id')
        active_model = self.env.context.get('active_model')
        if active_id and active_model == 'hr.employee':
            employee = self.env[active_model].browse(active_id)
            res.update({
                'employee_id': active_id,
                'partner_id': employee.address_home_id.id or
                employee.user_id.partner_id.id,
            })
        return res

    @api.multi
    def button_partner_select(self):
        self.employee_id.address_home_id = self.partner_id
        if self.env.context.get('create_ppe_picking'):
            self.employee_id.button_create_ppe_picking()
        return True
