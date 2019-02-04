# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from odoo.exceptions import ValidationError


class TestHrPayrollCancel(common.TransactionCase):

    def setUp(self):
        super(TestHrPayrollCancel, self).setUp()
        self.BankObj = self.env['res.partner.bank']
        self.HrEmpObj = self.env['hr.employee']
        self.HrPayslipObj = self.env['hr.payslip']
        self.partenr_id = self.ref('base.res_partner_12')
        self.bank_id = self.ref('base.res_bank_1')
        self.address_home_id = self.ref('base.res_partner_address_2')
        self.address_id = self.ref('base.res_partner_address_27')
        self.country_id = self.ref('base.in')
        self.department_id = self.ref('hr.dep_rd')

        self.res_partner_bank = self.BankObj.create({
            'acc_number': '001-9876543-21',
            'partner_id': self.partenr_id,
            'acc_type': 'bank',
            'bank_id': self.bank_id,
        })

        self.hr_employee_john = self.HrEmpObj.create({
            'address_home_id': self.address_home_id,
            'address_id': self.address_id,
            'birthday': '1984-05-01',
            'children': 0.0,
            'country_id': self.country_id,
            'department_id': self.department_id,
            'gender': 'male',
            'marital': 'single',
            'name': 'John',
            'bank_account_id': self.res_partner_bank.bank_id.id,
        })

        self.hr_payslip = self.HrPayslipObj.create({
            'name': 'Payslip of John',
            'employee_id': self.hr_employee_john.id,
        })

    def test_refund_sheet(self):
        self.hr_payslip.action_payslip_done()
        self.hr_payslip.refund_sheet()

        with self.assertRaises(ValidationError):
            self.hr_payslip.action_payslip_cancel()
        self.assertEqual(self.hr_payslip.refunded_id.state, 'done')
        self.hr_payslip.refunded_id.action_payslip_cancel()
        self.assertEqual(self.hr_payslip.refunded_id.state, 'cancel')
        self.assertEqual(self.hr_payslip.state, 'done')
        self.hr_payslip.action_payslip_cancel()
        self.assertEqual(self.hr_payslip.state, 'cancel')

    def test_action_payslip_cancel(self):
        self.hr_payslip.action_payslip_done()
        self.hr_payslip.refund_sheet()
        self.hr_payslip.move_id.journal_id.write({'update_posted': True})
        self.hr_payslip.refunded_id.action_payslip_cancel()
        self.hr_payslip.action_payslip_cancel()
