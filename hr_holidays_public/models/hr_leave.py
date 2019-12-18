# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# Copyright 2018 Brainbean Apps
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    holiday_type = fields.Selection(
        selection_add=[('public', 'Public Holidays')]
    )

    country_id = fields.Many2one(
        'res.country',
        'Country'
    )

    state_ids = fields.Many2many(
        'res.country.state',
        'hr_leave_state_rel',
        'leave_id',
        'state_id',
        'Related States'
    )

    _sql_constraints = [
        ('type_value', "CHECK(1=1)", "Remove Constraint"),
        ]

    @api.multi
    def action_validate(self):
        public = self.filtered(lambda h: h.holiday_type == 'public')
        no_public = self.filtered(lambda h: h.holiday_type != 'public')
        public.write({'state': 'validate'})
        for holiday in public:
            domain = []
            if holiday.country_id:
                domain = [
                    ('address_id.country_id', '=', holiday.country_id.id)
                ]
            if holiday.state_ids:
                domain.append((
                    'address_id.state_id', 'in', holiday.state_ids.ids
                ))
            employees = self.env['hr.employee'].search(domain)
            values = [holiday._prepare_holiday_values(employee) for employee in
                      employees]
            leaves = self.env['hr.leave'].with_context(
                tracking_disable=True,
                mail_activity_automation_skip=True,
                leave_fast_create=True,
                is_public_holidays=holiday.holiday_type == 'public',
                # is_public_holidays=False,
            ).create(values)
            leaves.action_approve()
        return super(HrLeave, no_public).action_validate()

    @api.onchange('holiday_type')
    def _onchange_type(self):
        if self.holiday_type == 'public':
            self.employee = False
            self.category_id = False
            self.mode_company_id = False
            self.department_id = False
        else:
            self.country_id = False
            self.state_ids = [(6, 0, [])]
            super()._onchange_type()

    def _get_number_of_days(self, date_from, date_to, employee_id):
        if (self.holiday_status_id.exclude_public_holidays or
                not self.holiday_status_id):
            instance = self.with_context(
                employee_id=employee_id,
                exclude_public_holidays=True,
            )
        else:
            instance = self
        return super(HrLeave, instance)._get_number_of_days(
            date_from,
            date_to,
            employee_id,
        )

    @api.multi
    def _create_resource_leave(self):
        public = self.filtered(
            lambda r: r.holiday_type == 'public'
        ).with_context(is_public_holidays=True)
        no_public = self.filtered(lambda r: r.holiday_type != 'public')
        super(HrLeave, public)._create_resource_leave()
        super(HrLeave, no_public)._create_resource_leave()
        return True
