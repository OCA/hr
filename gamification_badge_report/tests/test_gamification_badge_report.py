# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests.common as common


class TestHrCourse(common.TransactionCase):
    def test_query(self):
        self.env.cr.execute(self.env["gamification.badge.report"]._table_query)
        self.env.cr.dictfetchall()
