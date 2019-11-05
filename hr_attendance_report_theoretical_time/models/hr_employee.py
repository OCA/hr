# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def _compute_theoretical_hours_difference(self):
        data = self.env['hr.attendance.theoretical.time.report'].read_group(
            [('employee_id', 'in', self.ids)],
            ['worked_hours', 'theoretical_hours',
             'difference'], groupby='employee_id')
        for employee in self:
            record = list(filter(lambda d: d['employee_id'][0] == employee.id, data))
            if record:
                employee.theoretical_hours_difference = record[0]['difference']
                employee.theoretical_hours_difference_visible = True
            else:
                employee.theoretical_hours_difference_visible = False

    theoretical_hours_start_date = fields.Date(
        help="Fill this field for setting a manual start date for computing "
             "the theoretical hours independently from the attendances. If "
             "not filled, employee creation date or the calendar start date "
             "will be used (the greatest of both).",
    )
    theoretical_hours_difference = fields.Float(
        string="Theoretical Hours Difference",
        compute="_compute_theoretical_hours_difference"
    )
    theoretical_hours_difference_visible = fields.Boolean(
        string="Theoretical Hours Difference Smart Button Visible",
        compute="_compute_theoretical_hours_difference"
    )
