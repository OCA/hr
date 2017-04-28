# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    def _get_approvers_to_notify(self):
        """Defines who to notify."""
        company = self.employee_id.company_id
        if company.leave_notify_manager and self.employee_id.parent_id:
            return self.employee_id.parent_id
        else:
            return False

    @api.model
    def create(self, vals):
        res = super(HrHolidays, self).create(vals)
        res._notify_approvers()
        return res

    @api.one
    def _notify_approvers(self):
        """Input: res.user"""
        approvers = self._get_approvers_to_notify()
        if not approvers:
            return True
        for approver in approvers:
            self.add_follower(approver.id)
            if approver.user_id:
                self._message_auto_subscribe_notify(
                    [approver.user_id.partner_id.id])
        return True
