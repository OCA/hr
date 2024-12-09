from odoo.exceptions import ValidationError

from odoo.addons.base.tests.common import BaseCommon


class TestHRPhonePinPuk(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee_1 = cls.env["hr.employee"].create({"name": "Test employee 1"})

    def test_set_mobile_phone_pin(self):
        self.employee_1.mobile_phone_pin = "1234"
        self.assertEqual(self.employee_1.mobile_phone_pin, "1234")

    def test_set_mobile_phone_puk(self):
        self.employee_1.mobile_phone_puk = "12345678"
        self.assertEqual(self.employee_1.mobile_phone_puk, "12345678")

    def test_set_invalid_mobile_phone_pin(self):
        with self.assertRaises(ValidationError):
            self.employee_1.mobile_phone_pin = "123a"
        with self.assertRaises(ValidationError):
            self.employee_1.mobile_phone_pin = "123"

    def test_set_invalid_mobile_phone_puk(self):
        with self.assertRaises(ValidationError):
            self.employee_1.mobile_phone_puk = "1234567a"
        with self.assertRaises(ValidationError):
            self.employee_1.mobile_phone_puk = "1234567"
