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
    @api.depends('contract_ids', 'contract_ids.date_start', 'contract_ids.state')
    def _compute_first_contract_id(self):
        Contract = self.env['hr.contract']
        for employee in self:
            employee.first_contract_id = Contract.search(
                employee._get_contract_filter(),
                order='date_start asc',
                limit=1
            )

    @api.multi
    @api.depends('contract_ids', 'contract_ids.date_end', 'contract_ids.state')
    def _compute_last_contract_id(self):
        Contract = self.env['hr.contract']
        for employee in self:
            last_contract_id = self._get_last_contract_id(employee.id)
            employee.last_contract_id = Contract.browse(last_contract_id)
    
    @api.multi
    @api.onchange('service_hire_date')
    def _onchange_service_hire_date(self):  # pragma: no cover
        # Do nothing
        pass

    def _get_last_contract_id(self, employee_id):
        '''If the date_end of the contract is empty, need to take the date_start of this
        contract to avoid getting an empty date when sorting in descending order
        '''
        cr = self.env.cr
        query = '''SELECT c.id
                FROM hr_contract c
                WHERE c.employee_id = %s
                    AND c.state IN %s
                ORDER BY COALESCE(c.date_end, c.date_start) DESC
                LIMIT 1'''
        cr.execute(query, (employee_id, tuple(self._get_service_contract_states())))
        result = cr.fetchone()
        return result and result[0]
    
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
