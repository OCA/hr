# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import common


class TestHrEmployee(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.employee_admin = self.env.ref("hr.employee_admin")
        self.employee_admin.write({"birthday": "1990-05-15"})

    def test_compute_age(self):
        self.employee_admin._compute_age()
        age = relativedelta(fields.Date.today(), self.employee_admin.birthday).years
        self.assertEqual(self.employee_admin.age, age)
