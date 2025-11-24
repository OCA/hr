# Copyright 2025 Fundacion Esment - Estefanía Bauzá
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    appraisal_default_template_id = fields.Many2one(
        comodel_name="hr.appraisal.template",
        string="Default Appraisal Template",
        config_parameter="hr_appraisal_oca.default_appraisal_template_id",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Default template used for appraisals",
    )
