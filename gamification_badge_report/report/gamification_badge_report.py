# Copyright (C) 2020 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, tools


class GamificationBadgeReport(models.Model):

    _name = "gamification.badge.report"
    _description = "Gamification Badge Report"
    _auto = False
    _rec_name = "employee_id"

    employee_id = fields.Many2one("hr.employee", string="Employee")
    total = fields.Integer(string="Total")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """
                CREATE OR REPLACE VIEW gamification_badge_report AS (
                    select he.id as id, he.id as employee_id , count(gbu) as total
                    from gamification_badge_user as gbu
                    left join hr_employee as he on he.id = gbu.employee_id
                    group by he.id
                    order by total desc
                )
            """
        )
