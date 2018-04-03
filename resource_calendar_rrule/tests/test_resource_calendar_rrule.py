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
        self.calendar = self.env['resource.calendar'].create({
            'name': 'testcalendar',
        })

    def test_60_simplified_attendance(self):
        self.assertEqual(self.calendar.simplified_attendance['type'], 'null')
        self.calendar.write({
            'simplified_attendance':
            self.env['resource.calendar']._default_simplified_attendance(),
        })
        self.assertEqual(
            sum(map(
                lambda x: x['morning'] + x['afternoon'],
                self.calendar.simplified_attendance['data'],
            )),
            40
        )

    def test_61_stable_times(self):
        # test that times in a timezone with dst don't jump crossing borders
        self.env.user.write({'tz': 'Europe/Amsterdam'})
        self.calendar.write({
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
        intervals = self.calendar.get_working_intervals_of_day(
            fields.Datetime.from_string('2017-02-03 00:00:00'),
            fields.Datetime.from_string('2017-02-03 23:59:59'),
        )
        self.assertEqual(
            intervals,
            [[(datetime(2017, 2, 3, 8, 0), datetime(2017, 2, 3, 16, 0))]]
        )
        # but in summer, UTC+2
        intervals = self.calendar.get_working_intervals_of_day(
            fields.Datetime.from_string('2017-04-03 00:00:00'),
            fields.Datetime.from_string('2017-04-03 23:59:59'),
        )
        self.assertEqual(
            intervals,
            [[(datetime(2017, 4, 3, 7, 0), datetime(2017, 4, 3, 15, 0))]]
        )

    def test_62_negative_intervals(self):
        """ Test whether negative intervals are also allowed """
        # Create a test attendance of -40 hours in a week since 2016
        self.calendar.write({
            'attendance_ids': [(0, 0, {
                'name': 'testattendance',
                'rrule': [{
                    'type': 'rrule',
                    'freq': rrule.WEEKLY,
                    'interval': 1,
                    'byweekday': [0, 1, 2, 3, 4],
                    'dtstart': '2016-01-01 00:00:00',
                }],
                'hour_from': 17,
                'hour_to': 9,
            })],
        })
        # Check the working hours of a given monday in 2017
        intervals_before = self.calendar.get_working_intervals_of_day(
            fields.Datetime.from_string('2017-04-03 00:00:00'),
            fields.Datetime.from_string('2017-04-03 23:59:59'),
        )
        # Check that negative intervals are not removed
        self.assertGreaterEqual(len(intervals_before), 1)
        intervals_after = self.env['resource.calendar'].interval_remove_leaves(
            intervals_before[0][0], [])
        self.assertGreaterEqual(len(intervals_after), 1)
        # Check that the total amounts to -8 hours
        self.assertEquals((lambda a: a.days * 24 + a.seconds // 3600)(
            (intervals_after[0][1] - intervals_after[0][0])
            ), -8)

    def test_63_attendance_rrule_date_range(self):
        """ Test whether attendance rrule date range is respected """
        # Create a test attendance of 4 hours in a week *in 2016 only*
        self.calendar.write({
            'attendance_ids': [(0, 0, {
                'name': 'testattendance',
                'rrule': [{
                    'type': 'rrule',
                    'freq': rrule.WEEKLY,
                    'interval': 1,
                    'byweekday': [0, 1, 2, 3, 4],
                    'dtstart': '2016-01-01 00:00:00',
                    'until': '2016-12-31 23:59:59',
                }],
                'hour_from': 9,
                'hour_to': 13,
            })],
        })
        self.assertEquals(len(self.calendar.attendance_ids), 1)
        # Check the working hours of a given monday in 2016
        intervals = self.calendar.get_working_intervals_of_day(
            fields.Datetime.from_string('2016-04-04 00:00:00'),
            fields.Datetime.from_string('2016-04-04 23:59:59'),
        )
        self.assertEqual(
            intervals,
            [[(datetime(2016, 4, 4, 9, 0), datetime(2016, 4, 4, 13, 0))]]
        )
        # Check the working hours of a given monday in 2017
        intervals = self.calendar.get_working_intervals_of_day(
            fields.Datetime.from_string('2017-04-03 00:00:00'),
            fields.Datetime.from_string('2017-04-03 23:59:59'),
        )
        self.assertEqual(
            intervals,
            [[]]
        )
