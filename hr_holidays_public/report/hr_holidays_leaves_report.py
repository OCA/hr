# ©  2018 Fekete Mihai <feketemihai@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, tools


class HrHolidaysRemainingLeavesUser(models.Model):
    _inherit = "hr.holidays.remaining.leaves.user"

    no_of_leaves_hours = fields.Integer(
        'Remaining leaves hours', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr,
                                  'hr_holidays_remaining_leaves_user')
        self._cr.execute("""
            CREATE or REPLACE view hr_holidays_remaining_leaves_user as (
                 SELECT
                    min(hrs.id) as id,
                    rr.name as name,
                    sum(hrs.number_of_days) as no_of_leaves,
                    sum(hrs.number_of_hours) as no_of_leaves_hours,
                    rr.user_id as user_id,
                    hhs.name as leave_type
                FROM
                    hr_holidays as hrs, hr_employee as hre,
                    resource_resource as rr,hr_holidays_status as hhs
                WHERE
                    hrs.employee_id = hre.id and
                    hre.resource_id =  rr.id and
                    hhs.id = hrs.holiday_status_id
                GROUP BY
                    rr.name,rr.user_id,hhs.name
            )
        """)
