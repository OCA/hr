# -*- coding: utf-8 -*-

# Copyright (C) 2018 Compassion CH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
import datetime

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
        employee = self.env['hr.employee'].search([('id', '=', employee_id)])
        last_history_entry = self.env['hr.employee.balance.history'].search([
            ('employee_id', '=', employee.id),
            ('date', '<', str(datetime.date.today()))
        ], order='date desc', limit=1)

        start_date = None
        end_date = datetime.date.today()
        balance = None

        if last_history_entry:
            # One day after last period
            start_date = (datetime.datetime.strptime(last_history_entry.date, '%Y-%m-%d') +
                          datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            balance = last_history_entry.balance
        else:
            config = self.env['base.config.settings'].create({})
            start_date = config.get_beginning_date_for_balance_computation()
            balance = employee.initial_balance

        days, extra_hours_sum, _ = employee.complete_balance_computation(
            start_date=start_date,
            end_date=end_date,
            existing_balance=balance)

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
