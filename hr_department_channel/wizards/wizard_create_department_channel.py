# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class WizardCreateDepartmentChannel(models.TransientModel):

    _name = 'wizard.create.department.channel'

    name = fields.Char(required=True)

    @api.multi
    def generate_channel(self):
        department_id = self.env.context.get('active_id')
        department_id = self.env['hr.department'].browse(department_id)
        members = department_id.member_ids.mapped('user_id')
        if department_id.manager_id.user_id or False:
            members |= department_id.manager_id.user_id
        partners = members.mapped('partner_id')
        department_id.department_channel_ids = [(0, 0, {
            'name': self.name,
            'public': 'private',
            'channel_partner_ids': [
                (6, 0, partners.ids)
            ]
        })]
