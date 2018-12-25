# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    leave_allocation_ids = fields.One2many(
        string='Allocations',
        comodel_name='hr.leave.allocation',
        inverse_name='employee_id',
    )
    leave_request_ids = fields.One2many(
        string='Leaves',
        comodel_name='hr.leave',
        inverse_name='employee_id',
    )

    @api.multi
    def action_create_leave_allocation(self):  # pragma: no cover
        self.ensure_one()

        form_view = self.env.ref(
            'hr_holidays.hr_leave_allocation_view_form_manager'
        )

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.leave.allocation',
            'views': [[form_view.id, 'form']],
            'target': 'new',
            'context': {
                'default_employee_id': self.id,
            },
        }

    @api.multi
    def action_create_leave_request(self):  # pragma: no cover
        self.ensure_one()

        form_view = self.env.ref(
            'hr_holidays.hr_leave_view_form_manager'
        )

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.leave',
            'views': [[form_view.id, 'form']],
            'target': 'new',
            'context': {
                'default_employee_id': self.id,
            },
        }
