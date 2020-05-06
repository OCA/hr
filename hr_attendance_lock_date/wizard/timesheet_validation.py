# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class ValidationWizard(models.TransientModel):
    _inherit = 'timesheet.validation'

    @api.multi
    def action_validate(self):
        self.validation_line_ids.filtered('validate').mapped(
            'employee_id'
        ).write({'attendance_lock_date': self.validation_date})
        return super().action_validate()
