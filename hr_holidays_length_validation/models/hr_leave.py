# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api, _
from odoo.exceptions import UserError


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    @api.multi
    def _validate_length(self):
        self.ensure_one()

        if not self.employee_id:  # pragma: no cover
            return False

        recomputed_number_of_days = self.employee_id.get_work_days_data(
            self.date_from,
            self.date_to,
            domain=[
                ('time_type', '=', 'leave'),
                '|',
                ('holiday_id', '!=', self.id),
                ('holiday_id', '=', False),
            ],
        )['days']

        return self.number_of_days != recomputed_number_of_days

    @api.multi
    def action_validate_length(self):
        outdated = self.filtered(lambda x: x._validate_length())
        if outdated:
            raise UserError(_(
                'Following leaves have outdated length:\n\t %s'
            ) % (
                _('\n\t').join(list(map(
                    lambda leave: _('%s%s of %s for %.2f day(s)') % (
                        leave.holiday_status_id.name,
                        _(' (%s)') % (leave.name) if leave.name else '',
                        leave.employee_id.name,
                        leave.number_of_days,
                    ),
                    outdated
                ))),
            ))
