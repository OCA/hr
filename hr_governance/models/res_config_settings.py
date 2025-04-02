from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    governance_check_grayscale = fields.Boolean(
        string="Use GrayScale?",
        config_parameter="hr_governance.governance_check_grayscale",
    )
    governance_single_assignee_mode = fields.Boolean(
        string="Single Assignee Mode",
        config_parameter="hr_governance.governance_single_assignee_mode",
    )
