# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class HrHolidaysImposed(models.Model):
    _name = 'hr.holidays.imposed'
    _desc = 'Manage imposed holidays'

    name = fields.Char(required=True)
    date = fields.Date(required=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        string="Company",
        default=lambda self: self.env['res.company']._company_default_get(
            'hr.holidays.imposed')
    )
    status_id = fields.Many2one(
        comodel_name='hr.holidays.status',
        string="Leave type",
        required=True
    )
    employee_ids = fields.Many2many('hr.employee')
    auto_confirm = fields.Boolean()

    @api.multi
    def validate(self):
        for rec in self:
            created = self.env['hr.holidays']
            if rec.employee_ids:
                employees = rec.employee_ids
            else:
                employees = self.env['hr.employee'].search(
                    [('company_id', '=', rec.company_id.id)])

            for employee in employees:
                vals = {
                    'number_of_days_temp': 1.,
                    'name': rec.name,
                    'date_from': rec.date,
                    'date_to': rec.date,
                    'employee_id': employee.id,
                    'type': 'remove',
                    'holiday_status_id': rec.status_id.id,
                }

                created |= created.create(vals)
            if rec.auto_confirm:
                created.signal_workflow('validate')
