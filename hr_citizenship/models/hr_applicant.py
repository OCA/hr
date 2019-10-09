# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models, api


class Applicant(models.Model):
    _inherit = "hr.applicant"

    citizenship_ids = fields.One2many(
        comodel_name="res.citizenship",
        inverse_name="applicant_id",
        string="Multi citizenship",
    )

    @api.multi
    def create_employee_from_applicant(self):
        """ Link citizenship docs to new employee """
        super(Applicant, self).create_employee_from_applicant()
        for applicant in self:
            if applicant.citizenship_ids:
                applicant.emp_id.write({
                    'citizenship_ids': [(6, 0, applicant.citizenship_ids.ids)],
                })
