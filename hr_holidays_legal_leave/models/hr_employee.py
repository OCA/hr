# -*- coding: utf-8 -*-
# ©  2015 iDT LABS (http://www.@idtlabs.sl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields, _
from openerp.exceptions import Warning as UserError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def _inverse_remaining_days(self):
        self.ensure_one()
        legal_leave = self.company_id.legal_holidays_status_id
        if not legal_leave:
            raise UserError(_('Legal/annual leave type is not defined for '
                              'your company.'))
        diff = self.remaining_leaves - legal_leave.get_days(
            self.id)[legal_leave.id]['remaining_leaves']
        if diff > 0:
            leave = self.env['hr.holidays'].create(
                {
                    'name': 'Allocation for %s' % self.name,
                    'employee_id': self.id,
                    'holiday_status_id': legal_leave.id,
                    'type': 'add',
                    'holiday_type': 'employee',
                    'number_of_days_temp': diff
                }
            )
        elif diff < 0:
            raise UserError(_('You cannot reduce validated allocation '
                              'requests.'))

        for sig in ('confirm', 'validate', 'second_validate'):
            leave.signal_workflow(sig)

    @api.multi
    def _compute_remaining_days(self):
        for r in self:
            legal_leave = r.company_id.legal_holidays_status_id
            if not legal_leave:
                raise UserError(_('Legal/annual leave type is not defined for '
                                  'your company.'))
            r.remaining_leaves = legal_leave.get_days(
                r.id)[legal_leave.id]['remaining_leaves']

    remaining_leaves = fields.Integer(
        'Remaining Legal Leaves',
        compute='_compute_remaining_days',
        inverse='_inverse_remaining_days',
        help='Total number of legal leaves allocated to this employee. '
             'Change this value to create allocation/leave request. '
             'Total based on all the leave types without overriding limit.'
    )
