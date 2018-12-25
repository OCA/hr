# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    first_contract_id = fields.Many2one(
        'hr.contract',
        compute='_compute_first_contract_id',
        string='First Contract',
        help='First contract of the employee',
    )
    last_contract_id = fields.Many2one(
        'hr.contract',
        compute='_compute_last_contract_id',
        string='Last Contract',
        help='Last contract of the employee',
    )
    service_start_date = fields.Date(
        string='Start Date',
        readonly=True,
        related='first_contract_id.date_start',
    )
    service_termination_date = fields.Date(
        string='Termination Date',
        readonly=True,
        related='last_contract_id.date_end',
    )

    @api.multi
    @api.depends('contract_ids')
    def _compute_first_contract_id(self):
        Contract = self.env['hr.contract']
        for employee in self:
            employee.first_contract_id = Contract.search(
                employee._get_contract_filter(),
                order='date_start asc',
                limit=1
            )

    @api.multi
    @api.depends('contract_ids')
    def _compute_last_contract_id(self):
        Contract = self.env['hr.contract']
        for employee in self:
            employee.last_contract_id = Contract.search(
                employee._get_contract_filter(),
                order='date_end desc',
                limit=1
            )

    @api.multi
    @api.onchange('service_hire_date')
    def _onchange_service_hire_date(self):  # pragma: no cover
        # Do nothing
        pass

    @api.multi
    def _get_contract_filter(self):
        self.ensure_one()

        return [
            ('employee_id', '=', self.id),
            ('state', 'in', self._get_service_contract_states()),
        ]

    @api.model
    def _get_service_contract_states(self):
        return [
            'open',
            'pending',
            'close',
        ]
