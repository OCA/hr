# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.multi
    def _compute_leaves_count(self):
        leaves = self.env['hr.holidays'].read_group([
            ('employee_id', 'in', self.ids),
            ('holiday_status_id.limit', '=', False),
            ('state', '=', 'validate')],
            fields=['number_of_hours', 'employee_id'],
            groupby=['employee_id']
        )
        mapping = dict(
            [(leave['employee_id'][0], leave['number_of_hours'])
             for leave in leaves]
        )
        for employee in self:
            employee.leaves_count = mapping.get(employee.id)

    leaves_count = fields.Integer(
        'Number of Leaves',
        compute='_compute_leaves_count'
    )
    remaining_hours_ids = fields.One2many(
        'hr.holidays.remaining.leaves.user',
        'employee_id',
        string='Remaining hours per Leave Type'
    )
    holiday_ids = fields.One2many(
        'hr.holidays',
        'employee_id',
        string='Holidays'
    )
