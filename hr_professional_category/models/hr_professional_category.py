# Copyright 2021 César Fernández Domínguez
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrProfessionalCategory(models.Model):
    _name = "hr.professional.category"
    _description = "Professional Category"
    _order = "code, id"
    _rec_names_search = ["name", "code"]

    active = fields.Boolean(default=True)
    code = fields.Integer()
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        store=True,
        index=True,
    )

    def name_get(self):
        return [(x.id, "%d - %s" % (x.code, x.name)) for x in self]
