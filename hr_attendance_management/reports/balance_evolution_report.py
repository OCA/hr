# -*- coding: utf-8 -*-

# Copyright (C) 2018 Compassion CH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class BalanceEvolutionReport(models.TransientModel):

    _name = "balance.evolution.graph"

    day = fields.Date()
    employee_id = fields.Many2one('hr.employee', 'Employee')
    balance = fields.Float()

    @api.model
    def populate_graph(self, employee_id):
        """
        Creates the rows for the balance graph of given employee
        :param employee_id: the employee
        :return: True
        """
        last_cron_execution = self.env['base.config.settings'].create({}) \
            .get_last_balance_cron_execution()
        employee = self.env['hr.employee'].search([('id', '=', employee_id)])
        days, extra_hours_sum, _ = employee.complete_balance_computation(
            start_date=last_cron_execution,
            end_date=fields.Date.today(),
            existing_balance=employee.previous_period_balance)

        # delete previous graph for this employee to avoid miscalculation
        # for graph display
        self.env['balance.evolution.graph'].search([
            ('employee_id', '=', employee_id)
        ]).unlink()

        for i, day in enumerate(days):
            self.create({
                'employee_id': employee_id,
                'day': day,
                'balance': extra_hours_sum[i]
            })
        return True
