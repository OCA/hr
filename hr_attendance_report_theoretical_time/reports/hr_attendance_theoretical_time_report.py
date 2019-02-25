# Copyright 2017-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools
from datetime import datetime, time
from psycopg2.extensions import AsIs
from dateutil import tz


class HrAttendanceTheoreticalTimeReport(models.Model):
    _name = "hr.attendance.theoretical.time.report"
    _description = "Report of theoretical time vs attendance time"
    _auto = False
    _rec_name = 'date'
    _order = 'date,employee_id,theoretical_hours desc'

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string="Employee",
        readonly=True,
    )
    date = fields.Date(
        string="Date",
        readonly=True,
    )
    worked_hours = fields.Float(
        string='Worked',
        readonly=True,
    )
    theoretical_hours = fields.Float(
        string="Theoric",
        readonly=True,
    )
    difference = fields.Float(
        readonly=True,
    )

    def _select(self):
        # We put "max" aggregation function for theoretical hours because
        # we will recompute for other detail levels different than day
        # through recursivity by day results and will aggregate them manually
        return """
            min(id) AS id,
            employee_id,
            date,
            sum(worked_hours) AS worked_hours,
            max(theoretical_hours) AS theoretical_hours,
            sum(difference) AS difference
            """

    def _select_sub1(self):
        # Unique ID is assured (mostly, as we lose some precission) through
        # this MD5 hash converted to integer. See
        # https://stackoverflow.com/a/9812029 for details.
        return """
            (
                ('x'||substr(MD5('HA' || ha.id::text), 1, 8))::bit(32)::int
            ) AS id,
            ha.employee_id AS employee_id,
            ha.check_in::date AS date,
            ha.worked_hours AS worked_hours,
            ha.theoretical_hours AS theoretical_hours,
            0.0 AS difference
            """

    def _from_sub1(self):
        return """
            hr_attendance ha
            """

    def _where_sub1(self):
        return "True"

    def _select_sub2(self):
        # Same comment about ID uniqueness of sub1.
        return """
            (
                ('x'||substr(MD5(
                    'HE' || he.id::text || gs::text
                ), 1, 8))::bit(32)::int
            ) AS id,
            he.id AS employee_id,
            gs::date AS date,
            0 AS worked_hours,
            -1 AS theoretical_hours,
            0.0 AS difference
            """

    def _from_sub2(self):
        # We generate one record for each of the theoretical working days
        # since the employee creation / working schedule beginning for not
        # depending on the registered attendances.
        return """
                hr_employee he
            INNER JOIN
                resource_resource rr ON he.resource_id = rr.id
            LEFT JOIN
                resource_calendar_attendance rca
                    ON rca.calendar_id = rr.calendar_id
            CROSS JOIN
                generate_series(
                    greatest(
                        COALESCE(he.theoretical_hours_start_date,
                                 he.create_date::date),
                        COALESCE(rca.date_from,
                                 he.theoretical_hours_start_date,
                                 he.create_date::date)
                    )
                    + (8 + rca.dayofweek::int -
                        extract(dow from greatest(
                            COALESCE(he.theoretical_hours_start_date,
                                     he.create_date::date),
                            COALESCE(rca.date_from,
                                     he.theoretical_hours_start_date,
                                     he.create_date::date)
                        ))::int) % 7,
                    least(
                        COALESCE(rca.date_to, current_date),
                        current_date
                    )
                    + (-6 + rca.dayofweek::int -
                        extract(dow from least(
                            COALESCE(rca.date_to, current_date),
                            current_date
                        ))::int) % 7,
                    '7 days'
                ) AS gs
            """

    def _where_sub2(self):
        return """
            rca.id IS NOT NULL
            """

    def _group_by(self):
        return """
            employee_id,
            date
            """

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """
CREATE or REPLACE VIEW %s as (
    SELECT %s
    FROM (
        (
            SELECT %s
            FROM %s
            WHERE %s
        )
        UNION (
            SELECT %s
            FROM %s
            WHERE %s
        )
    ) AS u
    GROUP BY %s
)
            """, (
                AsIs(self._table),
                AsIs(self._select()),
                AsIs(self._select_sub1()),
                AsIs(self._from_sub1()),
                AsIs(self._where_sub1()),
                AsIs(self._select_sub2()),
                AsIs(self._from_sub2()),
                AsIs(self._where_sub2()),
                AsIs(self._group_by()),
            )
        )

    # TODO: To be activated for performance assuring cache clearing on changes
    # @tools.ormcache('employee.id', 'date')
    @api.model
    def _theoretical_hours(self, employee, date):
        """Get theoretical working hours for the day where the check-in is
        done for that employee.
        """
        date_date = fields.Datetime.from_string(date)
        if not employee.resource_id.calendar_id:
            return 0
        utz = self.env.user.tz
        return employee.with_context(
            exclude_public_holidays=True,
            employee_id=employee.id,
            leave_holiday_domain=[
                '|',
                ('holiday_id', '=', False),
                ('holiday_id.holiday_status_id.include_in_theoretical',
                 '=', False),
            ]
        ).get_work_days_data(
            datetime.combine(date_date, time(
                0, 0, 0, 0, tzinfo=tz.gettz(utz))),
            datetime.combine(
                date_date, time(23, 59, 59, 99999, tzinfo=tz.gettz(utz))
            ),
        )['hours']

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        """Compute dynamically theoretical hours amount, computing on the fly
        theoretical hours for non existing attendances with stored hours.
        This technique has proven to be more efficient than trying to call
        recursively `read_group` grouping by date and employee.
        """
        res = super(HrAttendanceTheoreticalTimeReport, self).read_group(
            domain, fields, groupby, offset=offset, limit=limit,
            orderby=orderby, lazy=lazy,
        )
        if 'theoretical_hours' not in fields:
            return res
        full_fields = all(x in fields for x in {
            'theoretical_hours',
            'worked_hours',
            'difference',
        })
        difference_field = 'difference' in fields
        for line in res:
            day_dict = {}
            records = self.search(line.get('__domain', domain))
            for record in records:
                key = (record.employee_id.id, record.date)
                if key not in day_dict:
                    if record.theoretical_hours < 0:
                        day_dict[key] = self._theoretical_hours(
                            record.employee_id.sudo(), record.date,
                        )
                    else:
                        day_dict[key] = record.theoretical_hours
            line['theoretical_hours'] = sum(day_dict.values())
            if full_fields:  # compute difference
                line['difference'] = (
                    (line['worked_hours'] or 0.0) - line['theoretical_hours']
                )
            elif difference_field:  # Remove wrong 0 values
                del line['difference']
        return res
