# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import ValidationError


class HrExpenseSheet(models.Model):
    _name = 'hr.expense.sheet'
    _inherit = ['hr.expense.sheet', 'tier.validation']
    _state_from = ['draft']
    _state_to = ['submit', 'approve']

    @api.multi
    def action_submit_sheet(self):
        if self.need_validation:
            if self.validated:
                super().action_submit_sheet()
            raise ValidationError(_('Please request a validation.'))
        super().action_submit_sheet()
