from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestHRPhonePinPuk(TransactionCase):
    def setUp(self):
        super(TestHRPhonePinPuk, self).setUp()
        self.employee_1 = self.env["hr.employee"].create({"name": "Employee 1"})

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
