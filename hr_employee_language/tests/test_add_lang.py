import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestAddLanguage(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestAddLanguage, cls).setUpClass()

    def test_add_lang(self):
        lang_list = self.env["res.lang"].search([("active", "in", (True, False))])
        lang_old = lang_list[0].code
        selection = self.env["hr.employee.language"]._get_selection()
        selection_ck = any(map(lambda t: lang_old in t, selection))
        # Test if a old lang is present
        self.assertEqual(selection_ck, True, "Old language is present")

        self.env["res.lang"].create({"code": "xx_XX", "name": "Foo"})
        selection = self.env["hr.employee.language"]._get_selection()
        selection_ck = any(map(lambda t: "xx_XX" in t, selection))
        # Test if a new lang is present
        self.assertEqual(selection_ck, True, "New language is present")

    def test_name_get(self):
        self.env["hr.employee.language"].create(
            {
                "name": "en_GB",
                "employee_id": self.env["hr.employee"].create({"name": "Test"}).id,
            }
        )
        self.env["hr.employee.language"].name_get()
        lang_ref = self.env["res.lang"].search(
            [("code", "=", "en_GB"), ("active", "in", (True, False))]
        )
        self.assertEqual(
            lang_ref.name,
            "English (UK)",
            "_compute_display_name not returns right value",
        )

    def test_name_get_with_inactive_lang(self):
        # Ensure that name_get works correctly with inactive languages
        self.env["res.lang"].create(
            {
                "code": "xx_XX",
                "name": "Test Language",
                "active": False,
            }
        )
        emp_lang = self.env["hr.employee.language"].create(
            {
                "name": "xx_XX",
                "employee_id": self.env["hr.employee"].create({"name": "Test"}).id,
            }
        )
        result = emp_lang.name_get()
        self.assertEqual(result[0][1], "Test Language")

    def test_name_get_missing_lang_code(self):
        # Test fallback when the language code is no longer present in res.lang.
        # The Selection field requires a valid value at create time, so we first
        # add the language, create the employee-language record, then delete the
        # language entry to simulate an orphaned / missing code.
        orphan_lang = self.env["res.lang"].create(
            {"code": "nx_NX", "name": "Nonexistent Language"}
        )
        emp_lang = self.env["hr.employee.language"].create(
            {
                "name": "nx_NX",
                "employee_id": self.env["hr.employee"].create({"name": "Test"}).id,
            }
        )
        # Remove the language to simulate a missing code
        orphan_lang.unlink()
        result = emp_lang.name_get()
        self.assertEqual(result[0][1], "nx_NX")  # Should fallback to code
