from odoo.tests.common import TransactionCase


class TestAddLanguage(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_add_lang(self):
        lang_list = self.env["res.lang"].search(
            [("active", "in", (True, False))], limit=1
        )
        lang_old = lang_list.code
        selection = self.env["hr.employee.language"]._get_selection()
        selection_ck = any(map(lambda t: lang_old in t, selection))
        # Test if a old lang is present
        self.assertEqual(selection_ck, True, "Old language is present")

        self.env["res.lang"].create({"code": "xx_XX", "name": "Foo"})
        selection = self.env["hr.employee.language"]._get_selection()
        selection_ck = any(map(lambda t: "xx_XX" in t, selection))
        # Test if a new lang is present
        self.assertEqual(selection_ck, True, "New language is present")

    def test_compute_display_name(self):
        record = self.env["hr.employee.language"].create(
            {
                "name": "en_GB",
                "employee_id": self.env["hr.employee"].create({"name": "Test"}).id,
            }
        )
        self.assertEqual(record.display_name, "English (UK)")
        lang_ref = self.env["res.lang"].search(
            [("code", "=", "en_GB"), ("active", "in", (True, False))], limit=1
        )
        self.assertEqual(
            lang_ref.name,
            "English (UK)",
            "_compute_display_name not returns right value",
        )
