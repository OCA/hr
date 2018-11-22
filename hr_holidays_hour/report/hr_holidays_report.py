# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from psycopg2.extensions import AsIs
import re

from odoo import fields, models, tools


class HrHolidaysRemainingLeavesUser(models.Model):
    _inherit = "hr.holidays.remaining.leaves.user"

    no_of_hours = fields.Float('Approved hours')
    virtual_hours = fields.Float('Virtual hours')
    no_of_leaves = fields.Integer('Remaining hours')
    employee_id = fields.Many2one('hr.employee', 'Employee')

    def _holidays_hour_select(self):
        return """
            sum(case when type='remove' and
                    extract(year from date_from) =
                    extract(year from current_date)
                then hrs.number_of_hours else 0 end) as no_of_hours,
            sum(case when (type='remove' and
                    extract(year from date_from) =
                    extract(year from current_date))
                then hrs.virtual_hours else 0 end) as virtual_hours,
            hre.id as employee_id
            """

    def _holidays_hour_group_by(self):
        return ", hre.id"

    def init(self):
        """Inject parts in the query with this hack, fetching the query and
        recreating it. Query is returned all in upper case and with final ';'.
        """
        super(HrHolidaysRemainingLeavesUser, self).init()
        cr = self._cr
        cr.execute("SELECT pg_get_viewdef(%s, true)", (self._table,))
        view_def = cr.fetchone()[0]
        view_def = view_def.replace("number_of_days", "number_of_hours")
        holidays_hour_select = self._holidays_hour_select()
        if holidays_hour_select not in view_def:
            # The 'leave_type' query could have case-sensitive expressions
            # It's better to use re here than the crude replace
            # (we basically search for "hhs.name AS leave_type")
            leave_type_query_part = re.compile(
                '.*,(.*?leave_type).*'
            ).match(' '.join(view_def.split('\n'))).groups()[0]
            view_def = view_def.replace(
                leave_type_query_part.strip(),
                "{},\n{}".format(
                    self._holidays_hour_select(),
                    leave_type_query_part
                ),
            )
        if view_def[-1] == ';':
            view_def = view_def[:-1]
        holidays_hour_group_by = self._holidays_hour_group_by()
        if holidays_hour_group_by not in view_def:
            view_def += self._holidays_hour_group_by()
        # Re-create view
        tools.drop_view_if_exists(cr, self._table)
        cr.execute(
            'CREATE OR REPLACE VIEW %s AS %s',
            (AsIs(self._table), AsIs(view_def))
        )
