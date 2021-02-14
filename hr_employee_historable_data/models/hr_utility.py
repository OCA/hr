# Copyright 2021 Iryna Vyshnevska (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import api, fields, models


class HrEmployeeWorkpermit(models.Model):
    _name = "hr.employee.workpermit"
    _inherit = "date.range"
    _description = "HR Employee Workpermit"
    _order = "date_start"

    name = fields.Char(required=False)
    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        required=True,
    )
    type_id = fields.Many2one("date.range.type")
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.user.company_id,
        string="Company",
    )
    visa = fields.Char(string="Visa No")
    permit_no = fields.Char(string="Permit No")


class HrEmployeeMarital(models.Model):
    _name = "hr.employee.marital"
    _inherit = "date.range"
    _description = "HR Employee Marital"
    _order = "date_start"

    name = fields.Char(required=False)
    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        required=True,
    )
    marital = fields.Selection(
        selection="_get_sort_options",
        required=True,
    )
    date_end = fields.Date(default=datetime.now().strftime("2100-01-01"))
    type_id = fields.Many2one("date.range.type")
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.user.company_id,
        string="Company",
    )

    @api.model
    def _get_sort_options(self):
        return self.env["hr.employee"].fields_get("marital")["marital"]["selection"]


class HrContractWage(models.Model):
    _name = "hr.contract.wage"
    _inherit = "date.range"
    _description = "HR Employee Workpermit"
    _order = "date_start"

    name = fields.Char(required=False)
    contract_id = fields.Many2one(
        comodel_name="hr.contract",
        required=True,
    )
    currency_id = fields.Many2one(string="Currency", related="contract_id.currency_id")
    wage = fields.Monetary("Wage", digits=(16, 2), required=True)
    type_id = fields.Many2one("date.range.type")
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.user.company_id,
        string="Company",
    )
