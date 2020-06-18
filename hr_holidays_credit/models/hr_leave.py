# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class HrLeave(models.Model):
    _inherit = "hr.leave"

    @api.constrains("state", "number_of_days", "holiday_status_id")
    def _check_holidays(self):
        uncreditable_requests = self.filtered(
            lambda holiday: not holiday._is_holiday_credit_allowed()
        )

        super(HrLeave, uncreditable_requests)._check_holidays()

    def _is_holiday_credit_allowed(self):
        self.ensure_one()

        leave_type = self.holiday_status_id

        if not leave_type.allow_credit:
            return False

        if self.employee_id in leave_type.creditable_employee_ids:
            return True

        if self.employee_id in (
            leave_type.creditable_employee_category_ids.mapped("employee_ids")
        ):
            return True

        if self.employee_id in (
            leave_type.creditable_department_ids.mapped("member_ids")
        ):
            return True

        return (
            not leave_type.creditable_employee_ids
            and not leave_type.creditable_employee_category_ids
            and not leave_type.creditable_department_ids
        )
