# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def pre_init_hook(cr):
    cr.execute(
        """
        ALTER TABLE hr_contract
            ADD amount numeric;
        COMMENT
            ON COLUMN hr_contract.amount
            IS 'Amount';
        ALTER TABLE hr_contract
            ADD amount_period varchar;
        COMMENT
            ON COLUMN hr_contract.amount_period
            IS 'Period of Amount';
        UPDATE hr_contract
            SET amount = wage, amount_period = 'month';
    """
    )


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    contracts = env["hr.contract"].search([])
    contracts._inverse_wage()
    contracts._compute_wage()
