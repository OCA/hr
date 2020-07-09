# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def pre_init_hook(cr):
    cr.execute(
        """
            ALTER TABLE hr_attendance
            ADD COLUMN IF NOT EXISTS time_changed_manually BOOLEAN
        """
    )
