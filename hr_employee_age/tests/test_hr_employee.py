# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.tests import common


class TestHrEmployee(common.TransactionCase):
    def setUp(self):
        super(TestHrEmployee, self).setUp()
        self.emp_root = self.env.ref('hr.employee_root')
        self.emp_root.write({
            'birthday': '1990-05-15'
        })

    def test_compute_age(self):
        self.emp_root._compute_age()
        age = relativedelta(
            fields.Date.from_string(fields.Date.today()),
            fields.Date.from_string(self.emp_root.birthday)).years
        self.assertEqual(self.emp_root.age, age)
