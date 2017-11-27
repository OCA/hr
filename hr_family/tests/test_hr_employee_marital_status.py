# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase
from ..hooks import post_init_hook


class TestHrEmployeeMaritalStatus(TransactionCase):
    def test_hr_employee_marital_status(self):
        post_init_hook(self.env.cr, self.env.registry)
        self.assertEqual(
            self.env.ref('hr.employee_fp').marital_status_id,
            self.env.ref('hr_family.married')
        )
        self.assertEqual(
            self.env.ref('hr_family.divorced').display_name,
            '[DIV] Divorced'
        )
