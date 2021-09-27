# Copyright 2021 Creu Blanca - Alba Riera

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_template pt
            SET is_ppe = TRUE, is_personal_equipment=TRUE
        FROM hr_employee_ppe_equipment as ppe_equipment
            INNER JOIN product_product as pp
            ON pp.id = ppe_equipment.product_id
        WHERE pp.product_tmpl_id = pt.id
        """,
    )
    if not openupgrade.column_exists(
        env.cr, "hr_personal_equipment_request", "old_ppe_id"
    ):
        openupgrade.logged_query(
            env.cr,
            """
                ALTER TABLE hr_personal_equipment_request
                ADD COLUMN old_ppe_id integer""",
        )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO hr_personal_equipment_request (
            employee_id,
            state,
            old_ppe_id
        )
        SELECT
            hr_ppe.employee_id,
            'accepted',
            hr_ppe.id
        FROM hr_employee_ppe hr_ppe""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO hr_personal_equipment (
            employee_id,
            state,
            product_id,
            start_date,
            expiry_date,
            indications,
            expire_ppe,
            certification,
            equipment_request_id,
            quantity,
            is_ppe,
            product_uom_id
        )
        SELECT
            hr_ppe.employee_id,
            'valid',
            ppe_equipment.product_id,
            hr_ppe.start_date,
            hr_ppe.expiry_date,
            hr_ppe.indications,
            hr_ppe.expire,
            hr_ppe.certification,
            pe_req.id,
            1,
            TRUE,
            pt.uom_id
        FROM hr_employee_ppe hr_ppe
            INNER JOIN hr_employee_ppe_equipment ppe_equipment
            ON ppe_equipment.id = hr_ppe.ppe_id
            INNER JOIN hr_personal_equipment_request pe_req
            ON pe_req.old_ppe_id = hr_ppe.id
            INNER JOIN product_product product
            ON product.id = ppe_equipment.product_id
            INNER JOIN product_template as pt
            ON product.product_tmpl_id = pt.id
        """,
    )
    env["hr.personal.equipment"].cron_ppe_expiry_verification()
