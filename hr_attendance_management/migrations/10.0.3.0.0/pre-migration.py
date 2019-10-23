# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2019 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Quentin Gigon <gigon.quentin@gmail.com>
#
#    The licence is in the file __manifest__.py
#
##############################################################################

from openupgradelib import openupgrade
from datetime import date


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return
    cr = env.cr

    cr.execute("ALTER TABLE hr_employee "
               "DROP COLUMN IF EXISTS previous_period_lost_hours")
    cr.execute("ALTER TABLE hr_employee "
               "DROP COLUMN IF EXISTS penultimate_period_lost_hours")
    cr.execute("ALTER TABLE hr_employee "
               "DROP COLUMN IF EXISTS penultimate_period_balance")
    cr.execute("ALTER TABLE hr_employee "
               "DROP COLUMN IF EXISTS previous_period_continuous_cap")
    cr.execute("ALTER TABLE hr_employee "
               "DROP COLUMN IF EXISTS previous_annual_balance")
    cr.execute("ALTER TABLE hr_employee "
               "DROP COLUMN IF EXISTS previous_period_balance CASCADE")
    cr.execute("ALTER TABLE hr_employee "
               "DROP COLUMN IF EXISTS last_update_balance")
    cr.execute("ALTER TABLE hr_employee "
               "DROP COLUMN IF EXISTS last_update_date")
    cr.execute("ALTER TABLE hr_employee "
               "DROP COLUMN IF EXISTS extra_hours")

    cr.execute("ALTER TABLE hr_employee "
               "ADD COLUMN IF NOT EXISTS limit_extra_hours Boolean")

    cr.execute("ALTER TABLE hr_employee RENAME COLUMN balance "
               "TO balance_copy")

    # cr.execute("""
    #     BEGIN
    #         IF EXISTS(SELECT *
    #             FROM hr_employee
    #             WHERE column_name='balance')
    #         THEN
    #             ALTER TABLE hr_employee RENAME COLUMN balance TO balance_copy;
    #         END IF;
    # """)

    cr.execute("SELECT id FROM hr_employee")
    employee_ids = cr.dictfetchall()
    for employee in employee_ids:
        cr.execute(
            """
                SELECT
                    extra_hours_continuous_cap
                FROM 
                    hr_employee
                WHERE
                    id = %s
            """, [employee["id"]])

        limit_extra_hours = cr.dictfetchone()["extra_hours_continuous_cap"]
        cr.execute("UPDATE hr_employee SET extra_hours_continuous_cap = %s "
                   "WHERE id = %s", (False, employee['id']))
        cr.execute("UPDATE hr_employee SET limit_extra_hours = %s "
                   "WHERE id = %s", (limit_extra_hours, employee['id']))
