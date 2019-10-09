# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class Citizenship(models.Model):
    _name = 'res.citizenship'
    _order = 'sequence'

    identification_id = fields.Char(
        string='Identification No',
    )
    country_id = fields.Many2one(
        comodel_name="res.country",
        string="Nationality (Country)",
        required=True,
    )
    passport_id = fields.Char(
        string="Passport No",
    )
    sequence = fields.Integer(string="Sequence")
    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        ondelete="cascade",
    )
    applicant_id = fields.Many2one(
        comodel_name="hr.applicant",
        ondelete="cascade",
    )

    _sql_constraints = [
        ('unique_country_employee', 'UNIQUE(country_id,employee_id)',
         'The Employee should have only one document per country'),
        ('unique_country_applicant', 'UNIQUE(country_id,applicant_id)',
         'The Applicant should have only one document per country'),
        ('check_relation',
         "CHECK( (applicant_id IS NOT NULL) or (employee_id IS NOT NULL))",
         'Applicant or Employee are mandatory'),
    ]
