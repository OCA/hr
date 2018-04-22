# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2 import IntegrityError
from openerp.tests.common import TransactionCase
from openerp import tools


class HrInputPayslipType(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(HrInputPayslipType, self).setUp(*args, **kwargs)
        self.obj_type = self.env[
            "hr.payslip.input_type"]

    @tools.mute_logger("openerp.sql_db")
    def test_no_duplicate(self):
        self.obj_type.create({
            "code": "X1",
            "name": "Example 1",
        })

        with self.assertRaises(IntegrityError):
            self.obj_type.create({
                "code": "X1",
                "name": "Example 1",
            })
