# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    department_channel_ids = fields.One2many(
        'mail.channel', readonly=True, string='Channels',
        inverse_name='department_id',
    )

    department_channel_count = fields.Integer(
        compute='_compute_department_channel_count',
        track_visibility='onchange',
    )

    @api.depends('department_channel_ids')
    def _compute_department_channel_count(self):
        for record in self:
            record.department_channel_count = len(
                record.department_channel_ids
            )

    def _add_employee_channel(self, employee):
        self.ensure_one()
        if not employee.user_id:
            return
        self.department_channel_ids.write({
            'channel_partner_ids': [(4, employee.user_id.partner_id.id)]
        })

    def _remove_employee_channel(self, employee):
        if not employee.user_id or (
            employee == self.manager_id and employee.department_id.id == self.id
        ):
            return
        self.department_channel_ids.write({
            'channel_partner_ids': [(3, employee.user_id.partner_id.id)]
        })

    @api.multi
    def write(self, vals):
        if 'manager_id' in vals:
            for record in self:
                if record.manager_id:
                    record._remove_employee_channel(record.manager_id)
        res = super().write(vals)
        if 'manager_id' in vals:
            for record in self:
                if record.manager_id:
                    record._add_employee_channel(record.manager_id)
        return res

    @api.multi
    def generate_channel(self):
        self.ensure_one()
        members = self.member_ids.mapped('user_id')
        if self.manager_id.user_id or False:
            members |= self.manager_id.user_id
        partners = members.mapped('partner_id')
        self.department_channel_ids = [(0, 0, {
            'name': self.name,
            'public': 'private',
            'channel_partner_ids': [
                (6, 0, partners.ids)
            ]
        })]
