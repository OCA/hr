# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.tools.float_utils import float_round


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    allow_credit = fields.Boolean(
        string='Allow Credit',
        help=(
            'If set to true, employees would be able to make requests for this'
            ' leave type even if allocated amount is insufficient.'
        ),
    )
    creditable_employee_ids = fields.Many2many(
        string='Creditable Employees',
        comodel_name='hr.employee',
        help='If set, limits credit allowance to specified employees',
    )
    creditable_employee_category_ids = fields.Many2many(
        string='Creditable Employee Tags',
        comodel_name='hr.employee.category',
        help=(
            'If set, limits credit allowance to employees with at least one of'
            ' specified tags'
        ),
    )
    creditable_department_ids = fields.Many2many(
        string='Creditable Departments',
        comodel_name='hr.department',
        help=(
            'If set, limits credit allowance to employees of specified'
            ' departments'
        ),
    )

    @api.multi
    def name_get(self):
        context_employee_id = self._context.get('employee_id')

        res = []
        for record in self:
            record_name = record.name

            extra = None
            if record.allocation_type != 'no' and context_employee_id:
                if record.virtual_remaining_leaves >= 0:
                    if record.allow_credit:
                        extra = _('%g available + credit')
                    else:
                        extra = _('%g available')
                    extra = extra % (
                        float_round(
                            record.virtual_remaining_leaves,
                            precision_digits=2
                        ) or 0.0,
                    )
                elif record.allow_credit:
                    extra = _('%g used in credit') % (
                        float_round(
                            -record.virtual_remaining_leaves,
                            precision_digits=2
                        ) or 0.0,
                    )

            if extra:
                record_name = _('%(name)s (%(extra)s)') % {
                    'name': record_name,
                    'extra': extra,
                }

            res.append((record.id, record_name))

        return res
