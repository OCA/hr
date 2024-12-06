# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import fields

from odoo.addons.base.tests.common import BaseCommon


class TestHrEmployee(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee_admin = cls.env.ref("hr.employee_admin")
        cls.employee_admin.write({"birthday": "1990-05-15"})

    def test_compute_age(self):
        self.employee_admin._compute_age()
        age = relativedelta(fields.Date.today(), self.employee_admin.birthday).years
        self.assertEqual(self.employee_admin.age, age)
