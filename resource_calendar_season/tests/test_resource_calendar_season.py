from datetime import datetime

from pytz import utc

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestResourceCalendarSeason(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResourceCalendar = cls.env["resource.calendar"]
        cls.standard = cls._create_calendar("Standard 40h", 8.0, 16.0)
        cls.summer = cls._create_calendar("Summer 35h", 8.0, 15.0)
        cls.seasonal = cls.ResourceCalendar.create(
            {
                "name": "Seasonal",
                "tz": "UTC",
                "is_seasonal": True,
                "default_calendar_id": cls.standard.id,
                "season_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Summer",
                            "season_calendar_id": cls.summer.id,
                            "month_from": "6",
                            "month_to": "9",
                        },
                    ),
                ],
            }
        )

    @classmethod
    def _create_calendar(cls, name, hour_from, hour_to):
        return cls.ResourceCalendar.create(
            {
                "name": name,
                "tz": "UTC",
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "name": f"{dayofweek}-{name}",
                            "dayofweek": str(dayofweek),
                            "hour_from": hour_from,
                            "hour_to": hour_to,
                            "day_period": "morning",
                        },
                    )
                    for dayofweek in range(5)
                ],
            }
        )

    def _hours(self, start, end):
        return self.seasonal.get_work_hours_count(
            utc.localize(start), utc.localize(end), compute_leaves=False
        )

    def test_winter_week_uses_default(self):
        hours = self._hours(datetime(2026, 1, 5), datetime(2026, 1, 10))
        self.assertEqual(hours, 40.0)

    def test_summer_week_uses_season(self):
        hours = self._hours(datetime(2026, 7, 6), datetime(2026, 7, 11))
        self.assertEqual(hours, 35.0)

    def test_range_crossing_boundary_sums_each_season(self):
        # Week of 2026-09-28: Mon-Wed (28-30 Sep) summer 7h, Thu/Fri (1-2 Oct) std 8h
        hours = self._hours(datetime(2026, 9, 28), datetime(2026, 10, 3))
        self.assertEqual(hours, 7.0 * 3 + 8.0 * 2)

    def test_season_calendar_resolution(self):
        self.assertEqual(
            self.seasonal._get_season_calendar(datetime(2026, 7, 1).date()),
            self.summer,
        )
        self.assertEqual(
            self.seasonal._get_season_calendar(datetime(2026, 12, 1).date()),
            self.standard,
        )

    def test_overlapping_seasons_raise(self):
        with self.assertRaises(ValidationError):
            self.seasonal.write(
                {
                    "season_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "Overlap",
                                "season_calendar_id": self.summer.id,
                                "month_from": "9",
                                "month_to": "10",
                            },
                        ),
                    ]
                }
            )

    def test_seasonal_requires_default(self):
        with self.assertRaises(ValidationError):
            self.ResourceCalendar.create({"name": "Bad seasonal", "is_seasonal": True})
