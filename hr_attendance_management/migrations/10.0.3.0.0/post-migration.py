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


# TODO this migration should work but if made in year 2020, it will not create a period for the year 2019
@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return
    cr = env.cr

    start_date = str(date.today().replace(year=2018, month=1, day=1))
    end_date = str(date.today().replace(year=2019, month=1, day=1))
    cr.execute("SELECT id FROM hr_employee")
    employee_ids = cr.dictfetchall()

    for employee in employee_ids:

        employee_model = env['hr.employee'].search([
            ('id', '=', employee["id"])
        ], limit=1)

        if employee_model:
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

            # Compute actual balance value of employee
            # without initial_balance taken into account
            employee_model.compute_balance()

            initial_balance = old_balance - employee_model.balance
            # Set initial balance of employee (represent balance before 01.01.2018)
            cr.execute("UPDATE hr_employee SET initial_balance = %s "
                       "WHERE id = %s",
                       (initial_balance, employee['id']))
            employee_model.initial_balance = initial_balance

            # Calculate extra and lost hours for 2018
            new_period_balance, new_period_lost = employee_model.past_balance_computation(start_date, end_date, 0)

            # Create a period for the year 2018
            employee_model.create_period(employee["id"],
                                         start_date,
                                         end_date,
                                         new_period_balance,
                                         initial_balance,
                                         new_period_lost,
                                         employee_model.extra_hours_continuous_cap)
