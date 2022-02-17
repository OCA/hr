# Copyright 2021 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2 import sql

from odoo import api, fields, models, tools

from ..models.hr_employee_hour import TYPE_SELECTION


class HrEmployeeHourReport(models.Model):
    _name = "hr.employee.hour.report"
    _auto = False  # Will be processed in init method
    _rec_name = "date"
    _order = "date, leave_type"

    date = fields.Date("Date")
    type = fields.Selection(TYPE_SELECTION, "Type")
    leave_type = fields.Char("Leave Type")
    employee_id = fields.Many2one("hr.employee", "Employee")
    manager_id = fields.Many2one("hr.employee", "Manager")
    user_id = fields.Many2one("res.users", "User")
    company_id = fields.Many2one("res.company", "Company")
    project_id = fields.Many2one("project.project", "Project")
    analytic_group_id = fields.Many2one("account.analytic.group")
    days_qty = fields.Float("Days")
    days_qty_abs = fields.Float("Days")
    hours_qty = fields.Float("Hours")
    hours_qty_abs = fields.Float("Hours")
    percentage = fields.Float("Percentage")

    @api.model
    def read_group(
        self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True
    ):
        # Add the percentage values
        # Force addition of this fields if not in the view specification
        needed_fields = ["hours_qty_abs", "hours_qty_abs:sum"]
        if not set(fields).intersection(set(needed_fields)):
            fields.append("hours_qty_abs:sum")
        result = super().read_group(
            domain, fields, groupby, offset, limit, orderby, lazy
        )

        if not result or not len(result) > 1:
            # Avoid processing if empty or only one result
            return result

        def get_grant_total(groups, key):
            """ Return the sum of this key's values for all records """
            return sum([rec.get(key, 0.0) for rec in groups])

        hours_total = get_grant_total(result, "hours_qty_abs")
        for rec in result:
            if hours_total:
                rec["percentage"] = (rec.get("hours_qty_abs", 0.0) / hours_total) * 100
        return result

    def select_hook_custom_fields(self):
        return ""

    def select_hook_leave_type(self):
        return """
            -- Specific leave type calculation
            heh.name AS leave_type,
        """

    def select_hook_negative_quantities(self):
        """ Must end with a comma if not empty """
        return f"""
            -- Inject negative value for total calculation
            SUM(CASE
                  WHEN heh.type = 'contract' THEN -heh.days_qty
                  ELSE heh.days_qty
            END) AS days_qty,
            SUM(CASE
                  WHEN heh.type = 'contract'  THEN -heh.hours_qty
                  ELSE heh.hours_qty
            END) AS hours_qty,
        """

    def select_hook_absolute_quantities(self):
        """ Must end with a comma if not empty """
        return f"""
            -- But keep absolute values for specific graph calculation
            SUM(heh.days_qty) AS days_qty_abs,
            SUM(heh.hours_qty) AS hours_qty_abs,
        """

    def _select(self):
        return f"""SELECT
            max(id) AS id,
            heh.project_id,
            heh.employee_id,
            heh.manager_id,
            heh.user_id,
            heh.company_id,
            heh.analytic_group_id,
            heh.date,
            heh.type,
            0.0 as percentage,
            {self.select_hook_leave_type()}
            {self.select_hook_negative_quantities()}
            {self.select_hook_absolute_quantities()}
            {self.select_hook_custom_fields()}""".rstrip().rstrip(
            ","
        )

    def _from(self):
        return """FROM hr_employee_hour AS heh"""

    def _where(self):
        return """WHERE type in ('contract', 'leave', 'timesheet')"""

    def group_by_hook_custom_fields(self):
        return ""

    def _group_by(self):
        return f"""GROUP BY
            heh.project_id,
            heh.employee_id,
            heh.manager_id,
            heh.user_id,
            heh.company_id,
            heh.analytic_group_id,
            heh.date,
            heh.name,
            heh.type,
            {self.group_by_hook_custom_fields()}""".rstrip().rstrip(
            ","
        )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self._cr.execute(
            sql.SQL(
                f"""CREATE or REPLACE VIEW {self._table} as (
            {self._select()}
            {self._from()}
            {self._where()}
            {self._group_by()}
        )"""
            )
        )
