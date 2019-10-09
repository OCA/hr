# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models, api


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    citizenship_ids = fields.One2many(
        comodel_name="res.citizenship",
        inverse_name="employee_id",
        string="Multi citizenship",
    )

    # override fields to update them with new model
    identification_id = fields.Char(
        compute="_compute_passport_data",
        store="True",
    )
    country_id = fields.Many2one(
        compute="_compute_passport_data"
    )
    passport_id = fields.Char(
        compute="_compute_passport_data"
    )

    @api.depends("citizenship_ids")
    def _compute_passport_data(self):
        """
        when documents added or their priority changed update employee card
        """
        for empl in self:
            if empl.citizenship_ids:
                item = empl.citizenship_ids[0]
                empl.update({
                    "identification_id": item.identification_id,
                    "country_id": item.country_id.id,
                    "passport_id": item.passport_id,
                })
