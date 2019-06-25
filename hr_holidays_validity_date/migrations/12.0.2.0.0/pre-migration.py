# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    if openupgrade.column_exists(
            cr,
            'hr_leave_type',
            'date_start'
    ):
        openupgrade.logged_query(
            cr, """
            UPDATE hr_leave_type
            SET validity_start = date_start, validity_stop = date_end;
            """
        )
