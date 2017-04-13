# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    def _get_approvers_to_notify(self):
        """Defines who to notify."""
        company = self.env['res.company']._company_default_get('hr.holidays')
        notify_to = company.leave_notify_approver
        if notify_to == 'none':
            return False
        elif notify_to == 'manager' and self.employee_id.parent_id:
            approvers = self.employee_id.parent_id.user_id
        elif (notify_to == 'department' and
                  self.employee_id.department_id.manager_id):
            approvers = self.employee_id.department_id.manager_id.user_id
        else:
            # also if notify_to == 'default' this will be run:
            approvers = self.env.ref('base.group_hr_manager').users
        return approvers

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
        for aprover in approvers:
            self.add_follower(aprover.id)
            self._message_auto_subscribe_notify([aprover.partner_id.id])
        return True
