# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    document_ids = fields.One2many(
        'ir.attachment',
        compute='_compute_document_ids',
        groups='hr.group_hr_user',
        string='Documents',
    )
    documents_count = fields.Integer(
        compute='_compute_document_ids',
        groups='hr.group_hr_user',
        string='Document Count',
    )

    def _compute_document_ids(self):
        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', self._name),
            ('res_id', 'in', self.ids),
        ])

        result = dict.fromkeys(self.ids, self.env['ir.attachment'])
        for attachment in attachments:
            result[attachment.res_id] |= attachment

        for employee in self:
            employee.document_ids = result[employee.id]
            employee.documents_count = len(employee.document_ids)

    @api.multi
    def action_get_attachment_tree_view(self):
        action = self.env.ref('base.action_attachment').read()[0]
        action['context'] = {
            'default_res_model': self._name,
            'default_res_id': self.ids[0]
        }
        action['domain'] = str([
            ('res_model', '=', self._name),
            ('res_id', 'in', self.ids),
        ])
        action['search_view_id'] = (
            self.env.ref('hr_employee_document.ir_attachment_view_search').id,
        )
        return action
