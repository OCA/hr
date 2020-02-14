# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if res.department_id:
            res.department_id._add_employee_channel(res)
        return res

    @api.multi
    def write(self, vals):
        if 'department_id' in vals or 'user_id' in vals:
            for record in self:
                if record.department_id:
                    record.department_id._remove_employee_channel(record)
        res = super().write(vals)
        if 'department_id' in vals or 'user_id' in vals:
            for record in self:
                if record.department_id:
                    record.department_id._add_employee_channel(record)
        return res
