# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class HrAccident(models.Model):
    _name = "hr.accident"
    _description = "Employee Accident"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        string="Reference",
        required=True,
        tracking=True,
    )
    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
        required=True,
        tracking=True,
    )
    date = fields.Date(
        required=True,
        tracking=True,
    )
    description = fields.Text()
    attachment_ids = fields.Many2many(
        comodel_name="ir.attachment",
        string="Documents",
    )
