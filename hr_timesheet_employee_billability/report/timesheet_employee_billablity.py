# Copyright (C) 2020 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta
import numpy
from odoo import tools
from odoo import api, fields, models


class TimesheetEmployeeBillablity(models.Model):
    _name = "timesheet.employee.billablity"
    _description = "Timehsheet Employee Billablity Reports"
    _auto = False
    _rec_name = 'employee_id'

    non_billable = fields.Float('Non Billable')
    billable = fields.Float('Billable')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    working_day = fields.Float('Working Day')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""",
                            (self._table, self._query()))

    def _query(self):
        partner_id = self.env.user.company_id.partner_id.id
        date = fields.Date.context_today(self)
        wk_start = date - timedelta(days=date.weekday())
        wk_end = wk_start + timedelta(days=6)
        holiday_num = numpy.busday_count(wk_start, wk_end)
        sql_query = """select
            min(pp.partner_id) as id,
            sum(
                case when pp.partner_id = %s then unit_amount else 0 end
            ) as non_billable,
            sum(case when pp.partner_id != %s or pp.partner_id IS NULL
            then unit_amount else 0 end) as billable,
            sum(case when pp.partner_id != %s or pp.partner_id IS NULL
            then unit_amount else 0 end)
            / sum(unit_amount) * 100 as total_per, sum(unit_amount) as total,
            sum(case when pp.partner_id != %s then unit_amount else 0 end)  /
            (%s - (SELECT count(number_of_days)
            FROM hr_leave as hl
            left join hr_employee as he on (he.id = hl.employee_id)
            WHERE
            (request_date_from >= '%s' AND request_date_from <= '%s')
            AND (request_date_to >= '%s' AND request_date_to <= '%s')
            AND state='validate' and employee_id = he.id) -
            (SELECT count(id) from hr_holidays_public_line
            WHERE date>= '%s' AND date<= '%s' ))
            as working_day,
            he.id as employee_id from account_analytic_line as aal
            left join project_project as pp on (pp.id = aal.project_id)
            left join hr_employee as he on (he.id = aal.employee_id)
            where project_id IS NOT NULL and aal.date >= '%s'
            and aal.date <= '%s'
            group by he.id""" % (partner_id,
                                 partner_id,
                                 partner_id,
                                 partner_id,
                                 int(holiday_num),
                                 str(wk_start),
                                 str(wk_end),
                                 str(wk_start),
                                 str(wk_end),
                                 str(wk_start),
                                 str(wk_end),
                                 str(wk_start),
                                 str(wk_end),)
        return sql_query
