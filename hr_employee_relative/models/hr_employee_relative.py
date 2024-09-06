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
    age_year = fields.Integer(string="Age (Years)", compute="_compute_age")
    age_month = fields.Integer(string="Age (Months)")
    age_day = fields.Integer(string="Age (Days)")

    job = fields.Char()
    phone_number = fields.Char()

    notes = fields.Text()

    @api.depends("date_of_birth")
    def _compute_age(self):
        for record in self:
            if record.date_of_birth:
                age = relativedelta(datetime.now(), record.date_of_birth)
                record.age_year = age.years
                record.age_month = age.months
                record.age_day = age.days
            else:
                record.age_year = 0
                record.age_month = 0
                record.age_day = 0

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if self.partner_id:
            self.name = self.partner_id.display_name
