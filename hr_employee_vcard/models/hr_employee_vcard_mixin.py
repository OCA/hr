from odoo import models
from odoo.tools.image import image_data_uri

FONT_FAMILY = {
    "lato": "'Lato', sans-serif",
    "roboto": "'Roboto', sans-serif",
    "open-sans": "'Open Sans', sans-serif",
    "montserrat": "'Montserrat', sans-serif",
    "oswald": "'Oswald', sans-serif",
    "raleway": "'Raleway', sans-serif",
    "tajawal": "'Tajawal', sans-serif",
    "fira-mono": "'Fira Mono', monospace",
}

IMAGE_FIELDS = {"logo", "qr"}

FRONT_FIELDS = {"logo", "company_name"}

FIELD_ICON = {
    "work_email": "fa-envelope",
    "work_phone": "fa-phone",
    "website": "fa-globe",
    "job_title": "fa-briefcase",
}


class HrEmployeeVcardMixin(models.AbstractModel):
    _name = "hr.employee.vcard.mixin"
    _description = "vCard Rendering Mixin"

    def _vcard_company(self):
        self.ensure_one()
        return self

    def _build_vcard_lines(self, values):
        self.ensure_one()
        front, back = [], []
        for field in self.vcard_layout_field_ids:
            field_name = field.field_name
            value = values.get(field_name)
            if not value:
                continue
            if field_name in IMAGE_FIELDS:
                line = {
                    "type": field_name,
                    "kind": "image",
                    "value": image_data_uri(value),
                }
            else:
                line = {
                    "type": field_name,
                    "kind": "text",
                    "value": value,
                    "icon": FIELD_ICON.get(field_name),
                }
            target = front if field_name in FRONT_FIELDS else back
            target.append(line)
        return front, back

    def _get_vcard_card_data(self, values):
        self.ensure_one()
        front_lines, back_lines = self._build_vcard_lines(values)
        return {
            "vcard_layout_id": self.vcard_layout_id,
            "front_lines": front_lines,
            "back_lines": back_lines,
            "font_family": FONT_FAMILY.get(self.vcard_layout_font, "inherit"),
            "background_style": self._get_vcard_background_style(),
        }

    def _get_vcard_background_style(self):
        self.ensure_one()
        record = self.with_context(bin_size=False)
        image = False
        if record.vcard_layout_background == "custom":
            image = record.vcard_layout_background_image
        elif record.vcard_layout_background == "demo-logo":
            image = record._vcard_company().logo
        if not image:
            return ""
        key = record.vcard_layout_id.view_id.key or ""
        overlay = (
            "rgba(31,43,58,0.72)"
            if key.endswith("modern")
            else "rgba(255,255,255,0.80)"
        )
        uri = image_data_uri(image)
        return (
            f"background-image:-webkit-linear-gradient({overlay},{overlay}),url({uri});"
        )
