# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def pre_init_hook(env):
    """Seed the rate of the existing contracts from their current wage.

    ``wage`` becomes a stored computed field derived from ``amount`` and
    ``amount_period``. Without this, installing the module on a database that
    already holds contracts would compute every wage from an empty amount and
    zero it. An amount that is already there always wins.
    """
    env.cr.execute(
        """
        ALTER TABLE hr_contract ADD COLUMN IF NOT EXISTS amount numeric;
        ALTER TABLE hr_contract ADD COLUMN IF NOT EXISTS amount_period varchar;
        UPDATE hr_contract
           SET amount = wage, amount_period = 'month'
         WHERE amount IS NULL;
        """
    )
