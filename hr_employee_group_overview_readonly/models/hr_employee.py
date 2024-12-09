from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    employee_cars_count = fields.Integer(
        compute="_compute_employee_cars_count",
        string="Cars",
        groups="""fleet.fleet_group_manager,
        hr_employee_group_overview_readonly.group_hr_overview_readonly""",
    )
