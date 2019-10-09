# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def migrate(cr, version=None):
    cr.execute(
        'alter table rel_employee_emergency_contact '
        'rename column employee_id to hr_employee_id'
    )
    cr.execute(
        'alter table rel_employee_emergency_contact '
        'rename column partner_id to res_partner_id'
    )
