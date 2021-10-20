# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade  # pylint: disable=W7936


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, "hr_course", "migrations/13.0.2.0.0/noupdate_changes.xml"
    )

    openupgrade.logged_query(
        env.cr,
        """
        SELECT setval('hr_course_schedule_id_seq', MAX(id))
        FROM hr_course_schedule
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
        SELECT setval('hr_course_id_seq', MAX(id))
        FROM hr_course
        """,
    )
