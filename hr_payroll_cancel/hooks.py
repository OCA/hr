# -*- coding: utf-8 -*-
# Copyright 2014 - Vauxoo http://www.vauxoo.com/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def post_init_hook(cr, registry):
    cr.execute("""UPDATE wkf_instance
        SET state = 'active'
        WHERE state = 'complete'
        and wkf_id = (SELECT id FROM wkf WHERE name = 'hr.payslip.basic')
        AND res_id IN (SELECT id FROM hr_payslip WHERE state = 'done')""")
