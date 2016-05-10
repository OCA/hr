# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    reference_ids = fields.Many2many(
        string="References",
        comodel_name="res.partner",
        rel="rel_employee_reference",
        column1="employee_id",
        column2="reference_id",
        domain=[
            ('is_company', '=', False),
            ]
        )
