# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    calendar_ids = fields.One2many(
        comodel_name="hr.employee.calendar",
        inverse_name="employee_id",
        string="Calendar planning",
    )

    def _regenerate_calendar(self):
        self.ensure_one()
        if not self.resource_calendar_id or self.resource_calendar_id.active:
            self.resource_calendar_id = self.env['resource.calendar'].create({
                'active': False,
                'name': _(
                    'Auto generated calendar for employee'
                ) + ' %s' % self.name,
                'attendance_ids': [],
            }).id
        else:
            self.resource_calendar_id.attendance_ids.unlink()
        vals_list = []
        for line in self.calendar_ids:
            for attendance_line in line.calendar_id.attendance_ids:
                data = attendance_line.copy_data({
                    'calendar_id': self.resource_calendar_id.id,
                    'date_from': line.date_start,
                    'date_to': line.date_end,
                })[0]
                vals_list.append((0, 0, data))
        self.resource_calendar_id.attendance_ids = vals_list

    def regenerate_calendar(self):
        self._regenerate_calendar()


class HrEmployeeCalendar(models.Model):
    _name = 'hr.employee.calendar'

    date_start = fields.Date(
        string="Start Date",
    )
    date_end = fields.Date(
        string="End Date",
    )
    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
        required=True,
    )
    calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        string="Working Time",
        required=True,
    )

    _sql_constraints = [
        ('date_consistency',
         'CHECK(date_start <= date_end)',
         'Date end should be higher than date start'),
    ]

    @api.model
    def create(self, vals):
        record = super(HrEmployeeCalendar, self).create(vals)
        record.employee_id._regenerate_calendar()
        return record

    @api.multi
    def write(self, vals):
        res = super(HrEmployeeCalendar, self).write(vals)
        for employee in self.mapped('employee_id'):
            employee._regenerate_calendar()
        return res

    @api.multi
    def unlink(self):
        employees = self.mapped('employee_id')
        res = super(HrEmployeeCalendar, self).unlink()
        for employee in employees:
            employee._regenerate_calendar()
        return res
