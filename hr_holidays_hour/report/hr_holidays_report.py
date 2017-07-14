# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, tools


class HrHolidaysRemainingLeavesUser(models.Model):
    _inherit = "hr.holidays.remaining.leaves.user"

    no_of_hours = fields.Float('Approved hours')
    virtual_hours = fields.Float('Virtual hours')
    no_of_leaves = fields.Integer('Remaining hours')
    employee_id = fields.Many2one('hr.employee', 'Employee')

    def init(self):
        cr = self._cr
        tools.drop_view_if_exists(cr, 'hr_holidays_remaining_leaves_user')
        cr.execute("""
            CREATE or REPLACE view hr_holidays_remaining_leaves_user as (
                 SELECT
                    min(hrs.id) as id,
                    rr.name as name,
                    sum(hrs.number_of_hours) as no_of_leaves,
                    sum(case when type='remove' and
                            extract(year from date_from) =
                            extract(year from current_date)
                        then hrs.number_of_hours else 0 end) as no_of_hours,
                    sum(case when (type='remove' and
                            extract(year from date_from) =
                            extract(year from current_date))
                        then hrs.virtual_hours else 0 end) as virtual_hours,
                    rr.user_id as user_id,
                    hhs.name as leave_type,
                    hre.id as employee_id
                FROM
                    hr_holidays as hrs, hr_employee as hre,
                    resource_resource as rr,hr_holidays_status as hhs
                WHERE
                    hrs.employee_id = hre.id and
                    hre.resource_id =  rr.id and
                    hhs.id = hrs.holiday_status_id
                GROUP BY
                    rr.name, rr.user_id, hhs.name, hre.id
            )
        """)
