# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class HrEmployeeRelative(models.Model):
    _name = "hr.employee.relative"
    _description = "HR Employee Relative"

    employee_id = fields.Many2one(comodel_name="hr.employee")
    relation_id = fields.Many2one("hr.employee.relative.relation", required=True)
    name = fields.Char(required=True)
    partner_id = fields.Many2one(
        "res.partner",
        domain=["&", ("is_company", "=", False), ("type", "=", "contact")],
    )
    gender = fields.Selection(
        selection=[("male", "Male"), ("female", "Female"), ("other", "Other")],
    )
    date_of_birth = fields.Date()
    age = fields.Float(compute="_compute_age")

    job = fields.Char()
    phone_number = fields.Char()

    notes = fields.Text()

    @api.depends("date_of_birth")
    def _compute_age(self):
        for record in self:
            age = relativedelta(datetime.now(), record.date_of_birth)
            record.age = age.years + (age.months / 12)

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if self.partner_id:
            self.name = self.partner_id.display_name
