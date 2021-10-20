# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade  # pylint: disable=W7936

_models_renames = [
    ("hr.course", "hr.course.schedule"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env, _models_renames)

    openupgrade.logged_query(
        env.cr,
        """
        SELECT id, name, category_id, permanence, permanence_time
        INTO hr_course
        FROM hr_course_schedule
        """,
    )

    openupgrade.logged_query(
        env.cr, "ALTER TABLE hr_course_schedule ADD course_id int4"
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_course_schedule
        SET course_id = id
        """,
    )
