import base64

from odoo.tests import Form, TransactionCase


class TestHrEmployeeVcard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Report = cls.env["ir.actions.report"]
        cls.company = cls.env.company
        cls.layout_modern = cls.env.ref(
            "hr_employee_vcard.hr_employee_vcard_layout_modern"
        )
        cls.layout_minimal = cls.env.ref(
            "hr_employee_vcard.hr_employee_vcard_layout_minimal"
        )
        cls.field_website = cls.env.ref(
            "hr_employee_vcard.hr_employee_vcard_field_website"
        )
        # A valid PNG to use as an uploaded image.
        cls.png = base64.b64encode(cls.Report.barcode("QR", "sample"))
        # Put the company in a known configuration.
        cls.company.write(
            {
                "vcard_layout_id": cls.layout_modern.id,
                "vcard_layout_background": "blank",
                "vcard_layout_font": "lato",
                "vcard_layout_field_ids": [
                    (6, 0, cls.env["hr.employee.vcard.field"].search([]).ids)
                ],
            }
        )
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Test Employee",
                "job_title": "Tester",
                "work_email": "test@example.com",
                "work_phone": "+1 000 000",
                "company_id": cls.company.id,
            }
        )

    # ------------------------------------------------------------------
    # Company / defaults
    # ------------------------------------------------------------------
    def test_new_company_defaults(self):
        company = self.env["res.company"].create({"name": "vCard Test Co"})
        self.assertEqual(company.vcard_layout_id, self.layout_modern)
        self.assertTrue(company.vcard_layout_field_ids)
        self.assertEqual(company.vcard_layout_background, "blank")
        self.assertEqual(company.vcard_layout_font, "lato")

    # ------------------------------------------------------------------
    # Line building (mixin)
    # ------------------------------------------------------------------
    def test_build_lines_front_back_split(self):
        values = self.company._get_vcard_preview_values()
        front, back = self.company._build_vcard_lines(values)
        front_types = [line["type"] for line in front]
        back_types = [line["type"] for line in back]
        self.assertIn("company_name", front_types)
        self.assertIn("name", back_types)
        self.assertNotIn("name", front_types)
        self.assertNotIn("company_name", back_types)

    def test_lines_adapt_to_selected_fields(self):
        self.company.vcard_layout_field_ids -= self.field_website
        values = self.company._get_vcard_preview_values()
        _front, back = self.company._build_vcard_lines(values)
        self.assertNotIn("website", [line["type"] for line in back])

    def test_lines_skip_empty_values(self):
        values = self.company._get_vcard_preview_values()
        values["work_email"] = False
        _front, back = self.company._build_vcard_lines(values)
        self.assertNotIn("work_email", [line["type"] for line in back])

    def test_contact_line_has_icon(self):
        values = self.company._get_vcard_preview_values()
        _front, back = self.company._build_vcard_lines(values)
        email = next(line for line in back if line["type"] == "work_email")
        self.assertEqual(email["kind"], "text")
        self.assertTrue(email["icon"])

    def test_image_line_is_data_uri(self):
        values = self.company._get_vcard_preview_values()
        _front, back = self.company._build_vcard_lines(values)
        qr = next(line for line in back if line["type"] == "qr")
        self.assertEqual(qr["kind"], "image")
        self.assertTrue(qr["value"].startswith("data:image/"))

    # ------------------------------------------------------------------
    # Card data (font / background)
    # ------------------------------------------------------------------
    def test_card_data_font_family(self):
        self.company.vcard_layout_font = "roboto"
        data = self.company._get_vcard_card_data(
            self.company._get_vcard_preview_values()
        )
        self.assertIn("Roboto", data["font_family"])

    def test_background_blank_is_empty(self):
        self.company.vcard_layout_background = "blank"
        self.assertEqual(self.company._get_vcard_background_style(), "")

    def test_background_custom_overlay(self):
        self.company.write(
            {
                "vcard_layout_background": "custom",
                "vcard_layout_background_image": self.png,
            }
        )
        style = self.company._get_vcard_background_style()
        self.assertIn("background-image", style)
        self.assertIn("linear-gradient", style)

    # ------------------------------------------------------------------
    # Employee: vCard content + QR + actions
    # ------------------------------------------------------------------
    def test_vcard_content(self):
        content = self.employee._get_vcard_content()
        self.assertTrue(content.startswith("BEGIN:VCARD"))
        self.assertTrue(content.strip().endswith("END:VCARD"))
        self.assertIn("FN:Test Employee", content)
        self.assertIn("EMAIL:test@example.com", content)

    def test_get_vcard_qr_is_png(self):
        qr = self.employee._get_vcard_qr()
        self.assertEqual(base64.b64decode(qr)[:4], b"\x89PNG")

    def test_action_generate_vcard(self):
        self.employee.vcard_qr = False
        action = self.employee.action_generate_vcard()
        self.assertTrue(self.employee.vcard_qr)
        self.assertEqual(action["type"], "ir.actions.report")
        self.assertEqual(action["report_name"], "hr_employee_vcard.report_vcard")

    def test_action_print_vcard(self):
        action = self.employee.action_print_vcard()
        self.assertEqual(action["report_name"], "hr_employee_vcard.report_vcard")

    # ------------------------------------------------------------------
    # Wizard
    # ------------------------------------------------------------------
    def test_wizard_onchange_sets_default_layout(self):
        self.company.vcard_layout_id = False
        wizard = self.env["hr.employee.vcard.wizard"].new(
            {"company_id": self.company.id}
        )
        wizard._onchange_company_id()
        self.assertTrue(wizard.vcard_layout_id)

    def test_wizard_preview_reacts_to_fields(self):
        form = Form(self.env["hr.employee.vcard.wizard"])
        self.assertIn("o_hr_employee_vcard_line_website", form.vcard_layout_preview)
        form.vcard_layout_field_ids.remove(id=self.field_website.id)
        self.assertNotIn("o_hr_employee_vcard_line_website", form.vcard_layout_preview)

    def test_wizard_preview_reacts_to_layout(self):
        form = Form(self.env["hr.employee.vcard.wizard"])
        form.vcard_layout_id = self.layout_minimal
        self.assertIn("o_hr_employee_vcard_minimal", form.vcard_layout_preview)

    # ------------------------------------------------------------------
    # Settings preview action
    # ------------------------------------------------------------------
    def test_settings_preview_action(self):
        settings = self.env["res.config.settings"].create({})
        action = settings.action_preview_vcard()
        self.assertEqual(
            action["report_name"], "hr_employee_vcard.report_vcard_preview"
        )

    # ------------------------------------------------------------------
    # Reports render (HTML, no wkhtmltopdf)
    # ------------------------------------------------------------------
    def test_report_vcard_html(self):
        html = self.Report._render_qweb_html(
            "hr_employee_vcard.report_vcard", self.employee.ids
        )[0]
        self.assertIn(b"o_hr_employee_vcard", html)
        self.assertIn(b'class="article"', html)

    def test_report_vcard_preview_html(self):
        html = self.Report._render_qweb_html(
            "hr_employee_vcard.report_vcard_preview", self.company.ids
        )[0]
        self.assertIn(b"o_hr_employee_vcard", html)
