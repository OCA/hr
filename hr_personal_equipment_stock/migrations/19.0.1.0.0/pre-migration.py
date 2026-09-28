# Copyright 2026 Giuseppe Borruso - Dinamiche Aziendali srl
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    # The old IDs point to procurement.group, while the new field with the same
    # name points to stock.reference. Keep the old values out of the new FK.
    cr.execute(
        """
        SELECT 1
          FROM information_schema.columns
         WHERE table_name = 'hr_personal_equipment_request'
           AND column_name = 'procurement_group_id'
        """
    )
    if cr.fetchone():
        cr.execute(
            """
            ALTER TABLE hr_personal_equipment_request
            RENAME COLUMN procurement_group_id TO procurement_group_id_18
            """
        )
