# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade  # pylint: disable=W7936


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(env.cr, "hr_course", "migration_course_id"):
        return
    openupgrade.logged_query(
        env.cr,
        """
            ALTER TABLE hr_course
            ADD COLUMN migration_course_id integer""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO hr_course (
            name,
            category_id,
            permanence,
            permanence_time,
            migration_course_id
        )
        SELECT name, category_id, permanence, permanence_time, id
        FROM hr_course_schedule
    """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_course_schedule hcs
        SET course_id = hc.id
        FROM hr_course hc
        WHERE hc.migration_course_id = hcs.id
    """,
    )
    openupgrade.load_data(
        env.cr, "hr_course", "migrations/14.0.2.0.0/noupdate_changes.xml"
    )
