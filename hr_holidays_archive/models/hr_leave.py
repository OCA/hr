# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    active = fields.Boolean(
        default=True,
    )

    @api.multi
    @api.constrains('active', 'state')
    def _check_active_state(self):
        for leave in self:
            if leave.active:
                continue
            if leave.state in ['confirm', 'validate1', 'validate']:
                raise ValidationError(_(
                    'Leave request archiving is not allowed in current status!'
                ))
