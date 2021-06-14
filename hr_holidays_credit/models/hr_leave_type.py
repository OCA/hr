# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.tools.float_utils import float_round


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    allow_credit = fields.Boolean(
        string="Allow Credit",
        help=(
            "If set to true, employees would be able to make requests for this"
            " leave type even if allocated amount is insufficient."
        ),
    )
    creditable_employee_ids = fields.Many2many(
        string="Creditable Employees",
        comodel_name="hr.employee",
        help="If set, limits credit allowance to specified employees",
    )
    creditable_employee_category_ids = fields.Many2many(
        string="Creditable Employee Tags",
        comodel_name="hr.employee.category",
        help=(
            "If set, limits credit allowance to employees with at least one of"
            " specified tags"
        ),
    )
    creditable_department_ids = fields.Many2many(
        string="Creditable Departments",
        comodel_name="hr.department",
        help=(
            "If set, limits credit allowance to employees of specified departments"
        ),
    )

    @api.multi
    def name_get(self):
        context_employee_id = self._context.get("employee_id")

        res = []
        for record in self:
            record_name = record.name

            extra = None
            if record.allocation_type != "no" and context_employee_id:
                amount = (
                    float_round(record.virtual_remaining_leaves,
                                precision_digits=2)
                    or 0.0
                )
                if amount >= 0:
                    if record.request_unit == "day":
                        if not record.allow_credit:
                            if abs(amount) <= 1:
                                extra = _("%g day available") % amount
                            else:
                                extra = _("%g days available") % amount
                        else:
                            if abs(amount) <= 1:
                                extra = _("%g day available + credit") % amount
                            else:
                                extra = _("%g days available + credit") % amount

                    elif record.request_unit == "hour":
                        if not record.allow_credit:
                            if abs(amount) <= 1:
                                extra = _("%g hour available") % amount
                            else:
                                extra = _("%g hours available") % amount
                        else:
                            if abs(amount) <= 1:
                                extra = _("%g hour available + credit") % amount
                            else:
                                extra = _("%g hours available + credit") % amount

                elif amount < 0:
                    amount = abs(amount)
                    if record.request_unit == "day":
                        extra = (
                            _("%g day used in credit") % amount
                            if abs(amount) <= 1
                            else _("%g days used in credit") % amount
                        )
                    elif record.request_unit == "hour":
                        extra = (
                            _("%g hour used in credit") % amount
                            if abs(amount) <= 1
                            else _("%g hours used in credit") % amount
                        )

            if extra:
                record_name = _("%(name)s (%(extra)s)") % {
                    "name": record_name,
                    "extra": extra,
                }

            res.append((record.id, record_name))

        return res
