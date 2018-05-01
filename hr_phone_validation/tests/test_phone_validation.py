from odoo.tests.common import TransactionCase


class TestHrPhoneValidation(TransactionCase):

    def test_phone_validation(self):
        employee = self.env['hr.employee'].search([], limit=1)
        phone = '+33612345678'
        employee.write({'work_phone': phone, 'mobile_phone': phone})
        employee._onchange_work_phone_validation()
        employee._onchange_mobile_phone_validation()

        self.assertEqual(employee.work_phone, '+33 6 12 34 56 78')
        self.assertEqual(employee.mobile_phone, '+33 6 12 34 56 78')
