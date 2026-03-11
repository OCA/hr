# Copyright 2026 Tecnativa - Vicent Castells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    cr.execute("""
        SELECT count(*)
        FROM information_schema.columns
        WHERE table_name='resource_calendar_attendance' AND column_name='date_from'
    """)
    if not cr.fetchone()[0]:
        _logger.info(">>> PRE-MIGRATION: No columns found. Skipping.")
        return
    cr.execute("""
        SELECT to_regclass('hr_employee_calendar')
    """)
    table_exists = cr.fetchone()[0]

    if not table_exists:
        _logger.info(
            ">>> PRE-MIGRATION: Target table hr_employee_calendar does not exist."
            "Backing up data to temporary table."
        )
        cr.execute("DROP TABLE IF EXISTS hr_employee_calendar_backup_data")
        cr.execute("""
            CREATE TABLE hr_employee_calendar_backup_data AS
            SELECT DISTINCT
                r.id as resource_calendar_id,
                a.date_from,
                a.date_to
            FROM resource_calendar_attendance a
            JOIN resource_calendar r ON a.calendar_id = r.id
            WHERE a.date_from IS NOT NULL OR a.date_to IS NOT NULL
        """)

    else:
        _logger.info("Target table exists. Migrating data directly.")
        cr.execute("""
            INSERT INTO hr_employee_calendar (
                employee_id,
                calendar_id,
                date_start,
                date_end,
                create_date,
                write_date,
                create_uid,
                write_uid
            )
            SELECT DISTINCT
                e.id,
                a.calendar_id,
                a.date_from,
                a.date_to,
                NOW() as create_date,
                NOW() as write_date,
                1 as create_uid,
                1 as write_uid
            FROM resource_calendar_attendance a
            JOIN hr_employee e ON e.resource_calendar_id = a.calendar_id
            WHERE (a.date_from IS NOT NULL OR a.date_to IS NOT NULL)
            AND NOT EXISTS (
                SELECT 1 FROM hr_employee_calendar existing
                WHERE existing.employee_id = e.id
                AND existing.calendar_id = a.calendar_id
                AND existing.date_start = a.date_from
                AND existing.date_end = a.date_to
            )
        """)

    _logger.info("MIGRATION: Data preservation completed.")
