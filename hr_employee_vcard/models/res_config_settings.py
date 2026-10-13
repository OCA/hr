from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    vcard_layout_id = fields.Many2one(
        related="company_id.vcard_layout_id",
        readonly=False,
    )

    vcard_layout_view_id = fields.Many2one(
        related="vcard_layout_id.view_id",
    )

    vcard_layout_background = fields.Selection(
        related="company_id.vcard_layout_background",
        readonly=False,
    )

    vcard_layout_background_image = fields.Binary(
        related="company_id.vcard_layout_background_image",
        readonly=False,
    )

    vcard_layout_font = fields.Selection(
        related="company_id.vcard_layout_font",
        readonly=False,
    )

    vcard_layout_field_ids = fields.Many2many(
        related="company_id.vcard_layout_field_ids",
        readonly=False,
    )

    def action_preview_vcard(self):
        self.ensure_one()
        return self.env.ref(
            "hr_employee_vcard.action_report_vcard_preview"
        ).report_action(self.company_id, config=False)
