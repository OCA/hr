# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime
from dateutil import rrule
from openerp import fields
from openerp.addons.resource.tests import test_resource


class TestResourceCalendarRrule(test_resource.TestResource):
    # first, we rerun resource's tests, resource.calendar.attendance#create
    # guarantees that the attendences created will have the correct rrules

    def setUp(self):
        super(TestResourceCalendarRrule, self).setUp()
        self.simplified_calendar = self.env['resource.calendar'].create({
            'name': 'testcalendar',
        })

    def test_90_simplified_attendance(self):
        self.assertFalse(self.simplified_calendar.simplified_attendance)
        self.simplified_calendar.write({
            'simplified_attendance':
            self.env['resource.calendar'].default_simplified_attendance(),
        })
        self.assertEqual(
            sum(map(
                lambda x: x['morning'] + x['afternoon'],
                self.simplified_calendar.simplified_attendance['data'],
            )),
            40
        )

    def test_91_stable_times(self):
        # test that times in a timezone with dst don't jump crossing borders
        self.env.user.write({'tz': 'Europe/Amsterdam'})
        self.simplified_calendar.write({
            'attendance_ids': [(0, 0, {
                'name': 'testattendance',
                'rrule': [{
                    'type': 'rrule',
                    'freq': rrule.WEEKLY,
                    'interval': 1,
                    'byweekday': [0, 1, 2, 3, 4],
                    'dtstart': '2016-12-31 23:00:00',
                }],
                'hour_from': 9,
                'hour_to': 17,
            })],
        })
        # in winter, this is UTC+1
        intervals = self.simplified_calendar.get_working_intervals_of_day(
            fields.Datetime.from_string('2017-02-03 00:00:00'),
            fields.Datetime.from_string('2017-02-03 23:59:59'),
        )
        self.assertEqual(
            intervals,
            [(datetime(2017, 2, 3, 8, 0), datetime(2017, 2, 3, 16, 0))]
        )
        # but in summer, UTC+2
        intervals = self.simplified_calendar.get_working_intervals_of_day(
            fields.Datetime.from_string('2017-04-03 00:00:00'),
            fields.Datetime.from_string('2017-04-03 23:59:59'),
        )
        self.assertEqual(
            intervals,
            [(datetime(2017, 4, 3, 7, 0), datetime(2017, 4, 3, 15, 0))]
        )
