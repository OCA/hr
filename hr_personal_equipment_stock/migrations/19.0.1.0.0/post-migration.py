# Copyright 2026 Giuseppe Borruso - Dinamiche Aziendali srl
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api
from odoo.fields import Command


def migrate(cr, version):
    cr.execute(
        """
        SELECT 1
          FROM information_schema.columns
         WHERE table_name = 'hr_personal_equipment_request'
           AND column_name = 'procurement_group_id_18'
        """
    )
    if not cr.fetchone():
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute(
        """
        SELECT id
          FROM hr_personal_equipment_request
         WHERE procurement_group_id_18 IS NOT NULL
           AND procurement_group_id IS NULL
        """
    )
    requests = (
        env["hr.personal.equipment.request"]
        .sudo()
        .browse([row[0] for row in cr.fetchall()])
    )
    for request in requests:
        reference = (
            env["stock.reference"]
            .sudo()
            .create({"name": request.name, "equipment_request_id": request.id})
        )
        request.procurement_group_id = reference
        request.line_ids.move_ids.sudo().write(
            {"reference_ids": [Command.link(reference.id)]}
        )

    cr.execute(
        """
        ALTER TABLE hr_personal_equipment_request
        DROP COLUMN procurement_group_id_18
        """
    )
