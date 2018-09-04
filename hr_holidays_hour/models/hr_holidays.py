# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class HrHolidays(models.Model):
    _inherit = "hr.holidays"

    @api.onchange('employee_id')
    def onchange_holiday_employee(self):
        self.department_id = None
        self.number_of_hours_temp = 0.0
        if self.employee_id:
            self._set_number_of_hours_temp()
            self.department_id = self.employee_id.department_id

    @api.onchange('date_from', 'date_to')
    def onchange_date(self):
        # Check in context what form is open: add or remove
        if self.env.context.get('default_type', '') == 'add':
            return

        self._check_dates()
        self._check_employee()
        self._set_number_of_hours_temp()

    @api.multi
    def _set_number_of_hours_temp(self):
        self.ensure_one()
        work_hours = self._compute_work_hours()
        self.number_of_hours_temp = work_hours

    @api.multi
    def _check_dates(self):
        self.ensure_one()
        # date_to has to be greater than date_from
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise UserError(_(
                    'The start date must be anterior to the end date.'
                ))

    @api.multi
    def _check_employee(self):
        self.ensure_one()
        employee = self.employee_id
        if not employee and (self.date_to or self.date_from):
            raise UserError(_('Set an employee first!'))

    @api.multi
    def _compute_work_hours(self):
        self.ensure_one()
        employee = self.employee_id
        work_hours = 0.0
        if self.date_from and self.date_to:
            from_dt = fields.Datetime.from_string(self.date_from)
            to_dt = fields.Datetime.from_string(self.date_to)
            emp_work_hours = employee.iter_work_hours_count(from_dt, to_dt)
            work_hours_data = [item for item in emp_work_hours]
            for index, (day, work_hours_count) in enumerate(work_hours_data):
                work_hours += work_hours_count
        return work_hours

    @api.depends('number_of_hours_temp', 'state')
    def _compute_number_of_hours(self):
        for rec in self:
            number_of_hours = rec.number_of_hours_temp
            if rec.type == 'remove':
                number_of_hours = -rec.number_of_hours_temp

            rec.virtual_hours = number_of_hours
            if rec.state not in ('validate',):
                number_of_hours = 0.0
            rec.number_of_hours = number_of_hours

    number_of_hours_temp = fields.Float(
        string='Allocation in Hours',
        digits=(2, 2),
        readonly=True,
        states={'draft': [('readonly', False)],
                'confirm': [('readonly', False)]}
    )
    number_of_hours = fields.Float(
        compute='_compute_number_of_hours',
        store=True
    )
    virtual_hours = fields.Float(
        compute='_compute_number_of_hours',
        store=True
    )
    working_hours = fields.Float(digits=(2, 2))

    @api.constrains(
        'holiday_type',
        'type',
        'employee_id',
        'holiday_status_id')
    def _check_holidays(self):
        for holiday in self:
            if holiday.holiday_type != 'employee' or holiday.type != 'remove':
                continue
            if holiday.employee_id and not holiday.holiday_status_id.limit:
                leave_hours = holiday.holiday_status_id.get_hours(
                    holiday.employee_id
                )
                holiday._check_leave_hours(leave_hours)

    @api.constrains('number_of_hours_temp')
    def _check_number_of_hours_temp(self):
        for holiday in self:
            if holiday.type == 'remove' and holiday.number_of_hours_temp < 0:
                raise ValidationError(
                    _('Hours of a leave request cannot be a negative number.')
                )

    @api.model
    def _check_leave_hours(self, leave_hours):
        remaining = leave_hours['remaining_hours']
        virt_remaining = leave_hours['virtual_remaining_hours']
        if remaining < 0 or virt_remaining < 0:
            # Raising a warning gives a more user-friendly
            # feedback than the default constraint error
            raise ValidationError(_(
                'The number of remaining hours is not sufficient for '
                'this leave type.\nPlease check for allocation requests '
                'awaiting validation.'))

    @api.multi
    def name_get(self):
        res = []
        for leave in self:
            res.append((leave.id, _("%s on %s : %.2f hour(s)") % (
                leave.employee_id.name,
                leave.holiday_status_id.name,
                leave.number_of_hours_temp
            )))
        return res

    @api.multi
    def _prepare_create_by_category(self, employee):
        self.ensure_one()
        values = super(HrHolidays, self)._prepare_create_by_category(employee)
        values.update({
            'number_of_hours_temp': self.number_of_hours_temp,
        })
        return values
