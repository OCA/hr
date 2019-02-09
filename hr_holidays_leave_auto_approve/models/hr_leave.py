# Copyright 2016-2019 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class HrLeave(models.Model):
    _inherit = "hr.leave"

    def _check_approval_update(self, state):
        if self.env.user._is_admin():
            return
        return super()._check_approval_update(state)

    @api.model
    def create(self, values):
        auto_approve = self._get_auto_approve_on_creation(values)
        tracking_disable = self.env.context.get('tracking_disable', False)
        tracking_disable = tracking_disable or auto_approve
        res = super(
            HrLeave, self.with_context(
                tracking_disable=tracking_disable)
            ).create(values)
        if res.can_approve and res.holiday_status_id.auto_approve:
            res.action_approve()
        return res

    @api.model
    def _get_auto_approve_on_creation(self, values):
        auto_approve = False
        if values.get('holiday_status_id'):
            auto_approve = self.env['hr.leave.type'].browse(
                values.get('holiday_status_id')
            ).auto_approve
        return auto_approve
