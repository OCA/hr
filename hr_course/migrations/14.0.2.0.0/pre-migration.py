# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade  # pylint: disable=W7936

_models_renames = [
    ("hr.course", "hr.course.schedule"),
]
_column_renames = {
    "hr_course_attendee": [("course_id", "course_schedule_id")],
}
_table_renames = [("hr_course", "hr_course_schedule")]


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.table_exists(env.cr, "hr_course_schedule"):
        return
    openupgrade.rename_models(env.cr, _models_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_columns(env.cr, _column_renames)
