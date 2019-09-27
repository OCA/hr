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


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return
    cr = env.cr

    cr.execute("SELECT id FROM hr_employee")
    employees = cr.dictfetchall()

    for employee in employees:
        # Get balance values
        cr.execute(
            """
                SELECT
                    temp_balance, balance
                FROM 
                    hr_employee
                WHERE
                    employee_id = %s
            """, (employee["id"]))

        temp_balance = cr.dictfetchone()["temp_balance"]
        old_balance = cr.dictfetchone()["balance"]

        # Initial balance is the diff between old one and new one
        initial_balance = old_balance - temp_balance

        cr.execute("UPDATE hr_employee SET initial_balance = %s "
                   "WHERE id = %s",
                   (initial_balance, employee['id']))

        cr.execute("UPDATE hr_employee SET balance = %s "
                   "WHERE id = %s",
                   (temp_balance, employee['id']))
        # Delete temporary row
        cr.execute("ALTER TABLE hr_employee "
                   "DROP COLUMN temp_balance")
