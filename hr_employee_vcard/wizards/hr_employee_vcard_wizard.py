from odoo import api, fields, models


class HrEmployeeVcardWizard(models.TransientModel):
    _name = "hr.employee.vcard.wizard"
    _inherit = "hr.employee.vcard.mixin"
    _description = "Employee vCard Wizard"

    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
        required=True,
    )

    vcard_layout_id = fields.Many2one(
        related="company_id.vcard_layout_id", readonly=False, required=True
    )

    vcard_layout_background = fields.Selection(
        related="company_id.vcard_layout_background", readonly=False, required=True
    )

    vcard_layout_background_image = fields.Binary(
        related="company_id.vcard_layout_background_image",
        readonly=False,
    )

    vcard_layout_font = fields.Selection(
        related="company_id.vcard_layout_font", readonly=False, required=True
    )

    vcard_layout_field_ids = fields.Many2many(
        related="company_id.vcard_layout_field_ids",
        readonly=False,
    )

    vcard_layout_preview = fields.Html(
        compute="_compute_vcard_layout_preview", sanitize=False
    )

    @api.onchange("company_id")
    def _onchange_company_id(self):
        for wizard in self:
            if not wizard.vcard_layout_id:
                wizard.vcard_layout_id = self.env["hr.employee.vcard.layout"].search(
                    [], order="sequence", limit=1
                )

    @api.depends(
        "vcard_layout_id",
        "vcard_layout_background",
        "vcard_layout_background_image",
        "vcard_layout_font",
        "vcard_layout_field_ids",
    )
    def _compute_vcard_layout_preview(self):
        for wizard in self:
            if wizard.vcard_layout_id:
                if wizard.env.context.get("bin_size"):
                    wizard = wizard.with_context(bin_size=False)
                wizard.vcard_layout_preview = wizard.env["ir.ui.view"]._render_template(
                    wizard._get_vcard_layout_template(),
                    wizard._get_vcard_layout_information(),
                )
            else:
                wizard.vcard_layout_preview = False

    def _vcard_company(self):
        self.ensure_one()
        return self.company_id

    def _get_vcard_layout_template(self):
        return "hr_employee_vcard.hr_employee_vcard_preview"

    def _get_vcard_layout_information(self):
        self.ensure_one()
        data = self._get_vcard_card_data(self.company_id._get_vcard_preview_values())
        data["preview_css"] = ""
        return data
