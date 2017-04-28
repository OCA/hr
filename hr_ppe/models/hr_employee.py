# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import _, api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    count_ppe_pickings = fields.Integer(
        string='# PPE pickings', compute='_compute_ppe_pickings')
    ppe_picking_ids = fields.Many2many(
        string='PPE pickings', comodel_name='stock.picking',
        relation='rel_employee_ppe_pickings', compute='_compute_ppe_pickings')
    ppe_move_ids = fields.Many2many(
        string='PPE moves', comodel_name='stock.move',
        relation='rel_employee_ppe_pickings', compute='_compute_ppe_pickings')

    @api.multi
    def ppe_pickings_from_employee(self, employee):
        picking_obj = self.env['stock.picking']
        ppe_type = self.env.ref('hr_ppe.hr_ppe_type')
        partners = employee.address_home_id | employee.user_id.partner_id
        return picking_obj.search([('partner_id', 'in', partners.ids),
                                   ('picking_type_id', '=', ppe_type.id)])

    @api.multi
    def _compute_ppe_pickings(self):
        for employee in self:
            employee.ppe_picking_ids = self.ppe_pickings_from_employee(
                employee)
            employee.count_ppe_pickings = len(employee.ppe_picking_ids)
            employee.ppe_move_ids = \
                employee.mapped('ppe_picking_ids.move_lines').filtered(
                    lambda m: m.state == 'done')

    @api.multi
    def button_open_ppe_pickings(self):
        self.ensure_one()
        ppe_picking_type = self.env.ref('hr_ppe.hr_ppe_type')
        pickings = self.ppe_pickings_from_employee(self)
        action = self.env.ref('stock.action_picking_tree_all')
        action = action.read()[0]
        action['domain'] = [('id', 'in', pickings.ids)]
        action['context'] = {
            'default_partner_id': self.address_home_id.id,
            'default_picking_type_id': ppe_picking_type.id,
        }
        return action

    @api.multi
    def create_ppe_picking(self):
        picking_obj = self.env['stock.picking']
        ppe_type = self.env.ref('hr_ppe.hr_ppe_type')
        for employee in self.filtered(lambda e: e.mapped('job_id.ppe_ids')):
            ppes = employee.mapped('job_id.ppe_ids')
            picking = picking_obj.create({
                'partner_id': employee.address_home_id.id,
                'picking_type_id': ppe_type.id,
                'move_lines': [(0, 0, {
                    'name': '{} {} {}'.format(
                        x.product_id.name, _('for job title'), x.job_id.name),
                    'product_id': x.product_id.id,
                    'product_uom': x.product_uom_id.id,
                    'product_uom_qty': x.product_uom_qty,
                    'location_id': ppe_type.default_location_src_id.id,
                    'location_dest_id': ppe_type.default_location_dest_id.id,
                }) for x in ppes]
            })
            picking.action_confirm()

    @api.multi
    def button_create_ppe_picking(self):
        self.ensure_one()
        if not self.job_id.ppe_ids:
            action = self.env.ref('hr.action_hr_job')
            action = action.read()[0]
            action.update({
                'view_mode': u'form,tree',
                'views': [],
                'res_id': self.job_id.id,
            })
            return action
        if not self.address_home_id:
            action = self.env.ref(
                'hr_ppe.hr_employee_partner_selection_wizard_action')
            action = action.read()[0]
            action['context'] = {
                'active_id': self.id,
                'active_model': self._model._name,
                'create_ppe_picking': True,
            }
            return action
        self.create_ppe_picking()
