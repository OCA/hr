# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from psycopg2.extensions import AsIs

from odoo import fields, models, tools


class LeaveReport(models.Model):
    _inherit = 'hr.leave.report'

    number_of_hours = fields.Float('Duration (hours)', readonly=True)

    def _leaves_holidays_hour_select(self):
        return """
            leaves.number_of_hours,
            """

    def _allocation_holidays_hour_select(self):
        return """
            allocation.number_of_hours,
            """

    def _request_holidays_hour_select(self):
        return """
            request.number_of_hours * '-1'::integer::double precision AS
                number_of_hours,
            """

    def init(self):
        """Inject parts in the query with this hack, fetching the query and
        recreating it. Query is returned all in upper case and with final ';'.
        """
        super().init()
        cr = self._cr
        cr.execute("SELECT pg_get_viewdef(%s, true)", (self._table,))
        view_def = cr.fetchone()[0]
        view_def = view_def.replace(
            "leaves.number_of_days",
            "{} leaves.number_of_days".format(
                self._leaves_holidays_hour_select()),
        )
        view_def = view_def.replace(
            "allocation.number_of_days",
            "{} allocation.number_of_days".format(
                self._allocation_holidays_hour_select()),
        )
        view_def = view_def.replace(
            "request.number_of_days",
            "{} request.number_of_days".format(
                self._request_holidays_hour_select()),
        )
        if view_def[-1] == ';':
            view_def = view_def[:-1]
        # Re-create view
        tools.drop_view_if_exists(cr, self._table)
        cr.execute('create or replace view %s as (%s)', (
            AsIs(self._table), AsIs(view_def),
        ))
