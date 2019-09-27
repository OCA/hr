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

    start_date = str(date.today().replace(year=2018, month=1, day=1))
    # Chose this day because its one of the date of execution of the CRON
    end_date = str(date.today().replace(year=2019, month=5, day=24))
    cr.execute("SELECT id FROM hr_employee")
    employee_ids = cr.dictfetchall()

    for employee in employee_ids:

        employee_model = env['hr.employee'].search([
            ('id', '=', employee["id"])
        ], limit=1)

        if employee_model:
            new_balance, lost = employee_model.past_balance_computation(start_date, end_date, 0)

            # Get old balance value
            cr.execute(
                """
                    SELECT
                        balance
                    FROM 
                        hr_employee
                    WHERE
                        id = %s
                """, [employee["id"]])

            old_balance = cr.dictfetchone()["balance"]

            # Initial balance is the diff between old one and new one
            initial_balance = old_balance - new_balance

            cr.execute("UPDATE hr_employee SET initial_balance = %s "
                       "WHERE id = %s",
                       (initial_balance, employee['id']))

            cr.execute("UPDATE hr_employee SET balance = %s "
                       "WHERE id = %s",
                       (new_balance, employee['id']))
