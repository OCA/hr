# -*- coding: utf-8 -*-
# © 2016 ONESTEiN BV (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class HrHolidays(models.Model):
    _inherit = "hr.holidays"

    @api.model
    def _check_state_access_right(self, vals):
        if self.env['res.users'].browse(self.env.uid)._is_admin():
            return True
        return super(HrHolidays, self)._check_state_access_right(vals)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, values):
        result = super(HrHolidays, self).create(values)
        if result.holiday_status_id.auto_approve:
            result.sudo().signal_workflow('validate')
        return result
