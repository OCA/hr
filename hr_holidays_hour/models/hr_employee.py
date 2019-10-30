# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.multi
    def _compute_leaves_count(self):
        leaves = self.env['hr.leave'].read_group([
            ('employee_id', 'in', self.ids),
            ('holiday_status_id.allocation_type', '!=', 'no'),
            ('state', '=', 'validate')],
            fields=['number_of_hours', 'employee_id'],
            groupby=['employee_id']
        )
        mapping_leaves = dict(
            [(leave['employee_id'][0], leave['number_of_hours'])
             for leave in leaves]
        )
        allocations = self.env['hr.leave.allocation'].read_group([
            ('employee_id', 'in', self.ids),
            ('holiday_status_id.allocation_type', '!=', 'no'),
            ('state', '=', 'validate')],
            fields=['number_of_hours', 'employee_id'],
            groupby=['employee_id']
        )
        mapping_allocations = dict(
            [(allocation['employee_id'][0], allocation['number_of_hours'])
             for allocation in allocations]
        )
        for employee in self:
            employee.leaves_count = \
                mapping_allocations.get(employee.id, 0) - \
                mapping_leaves.get(employee.id, 0)

    leaves_count = fields.Float(
        'Number of Leaves',
        compute='_compute_leaves_count'
    )

    def _get_remaining_leaves(self):
        """ Helper to compute the remaining leaves for the current employees
            :returns dict where the key is the employee id, and the value is
            the remain leaves
        """
        self._cr.execute("""
            SELECT
                sum(h.number_of_hours) AS hours,
                h.employee_id
            FROM
                (
                    SELECT holiday_status_id, number_of_hours,
                        state, employee_id
                    FROM hr_leave_allocation
                    UNION
                    SELECT holiday_status_id,
                           (number_of_hours * -1) as number_of_hours,
                           state,
                           employee_id
                    FROM hr_leave
                ) h
                join hr_leave_type s ON (s.id=h.holiday_status_id)
            WHERE
                h.state='validate' AND
                (s.allocation_type='fixed' OR
                 s.allocation_type='fixed_allocation') AND
                h.employee_id in %s
            GROUP BY h.employee_id""", (tuple(self.ids),))
        return dict((row['employee_id'], row['hours'])
                    for row in self._cr.dictfetchall())
