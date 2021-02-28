# Copyright 2020 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl

from datetime import datetime, timedelta

from odoo.tests import SavepointCase


class TestHREmployeePPE(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestHREmployeePPE, cls).setUpClass()
        cls.hr_employee_ppe = cls.env["hr.employee.ppe"]
        cls.hr_employee_ppe_equipment = cls.env["hr.employee.ppe.equipment"]
        cls.hr_employee_ppe1 = cls.env.ref("hr_employee_ppe.hr_employee_ppe1")
        cls.hr_employee_ppe2 = cls.env.ref("hr_employee_ppe.hr_employee_ppe2")

    def test_hr_employee_ppe(self):
        self.hr_employee_ppe1._compute_status()
        self.assertEqual(self.hr_employee_ppe1.status, "expired")

        self.hr_employee_ppe1.status = "valid"
        self.env["hr.employee.ppe"].cron_ppe_expiry_verification()
        self.assertEqual(self.hr_employee_ppe1.status, "expired")

        self.hr_employee_ppe1.end_date = (datetime.now() + timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )
        self.hr_employee_ppe1._compute_status()
        self.assertEqual(self.hr_employee_ppe1.status, "valid")

        self.hr_employee_ppe2._compute_status()
        self.assertEqual(self.hr_employee_ppe2.status, "valid")

        self.hr_employee_ppe1._compute_name()
        self.assertEqual(
            self.hr_employee_ppe1.name, "Mask for COVID-19 to Abigail Peterson"
        )
        self.assertEqual(self.hr_employee_ppe1.expire, True)
