# -*- coding: utf-8 -*-

# Copyright (C) 2018 Compassion CH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import tools
from odoo import models, fields, api


class ExtraHoursEvolutionDayReport(models.Model):
    _name = "hr.attendance.balance.evolution.report"
    _table = "extra_hours_evolution_day_report"
    _description = "Extra hours evolution by days"
    _auto = False
    _rec_name = 'hr_date'

    hr_date = fields.Char(string="Date", readonly=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', readonly=True)
    balance = fields.Float()

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(
            self.env.cr, self._table)

        self.env.cr.execute("""
            CREATE OR REPLACE VIEW extra_hours_evolution_day_report AS
            SELECT sub_2.id,
                   sub_2.hr_date,
                   sub_2.employee_id,
                   sub_2.balance + sub_2.annual_balance AS balance
            FROM
              (SELECT sub.hr_date AS hr_date,
                      ROW_NUMBER() OVER (ORDER BY (SELECT 100)) AS id,
                      sum(sub.extra_hours) OVER (PARTITION BY sub.employee_id
                          ORDER BY sub.hr_date) AS balance,
                      sub.employee_id AS employee_id,
                      sub.annual_balance
               FROM
                 (SELECT hr.date AS hr_date,
                         sum(hr.extra_hours) AS extra_hours,
                         hr.employee_id AS employee_id,
                         COALESCE(max(e.annual_balance), 0.0) AS annual_balance
                  FROM hr_attendance_day AS hr
                  JOIN hr_employee e ON hr.employee_id = e.id
                  WHERE hr.date < now()
                    AND hr.date >= date_trunc('year', now())
                  GROUP BY hr_date,
                           hr.employee_id
                  ORDER BY hr_date) AS sub
               ORDER BY hr_date,
                        employee_id) AS sub_2
        """)
