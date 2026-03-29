from odoo.tests.common import TransactionCase
from odoo import fields


class TestWellnessDashboard(TransactionCase):
    def setUp(self):
        super(TestWellnessDashboard, self).setUp()
        self.Dashboard = self.env["wellness.dashboard"]
        self.Check = self.env["wellness.check"]

        # Ensure we work with the singleton
        self.singleton = self.Dashboard.search([], limit=1)
        if not self.singleton:
            self.singleton = self.Dashboard.create({})

    def test_dashboard_stats_calculation(self):
        """Verify that dashboard stats summarize daily activity correctly."""
        today = fields.Date.today()

        # Create different sentiments
        self.Check.create({"mood_score": 10, "sentiment": "happy", "date": today})
        self.Check.create({"mood_score": 5, "sentiment": "neutral", "date": today})
        self.Check.create({"mood_score": 3, "sentiment": "sad", "date": today})

        stats = self.Check.get_wellness_stats()

        # 3 participants, avg mood: (10+5+3)/3 = 6.0
        self.assertEqual(stats["participation_today"], 3)
        self.assertEqual(stats["avg_mood_today"], 6.0)
        self.assertEqual(stats["sign"], "stable")  # happy count == sad count

    def test_pulse_refresh_logic(self):
        """Test the manual refresh logic in the dashboard record."""
        self.Check.create({"mood_score": 10, "sentiment": "happy"})

        # Trigger refresh
        self.singleton._refresh_pulse()

        self.assertEqual(self.singleton.participation_today, 1)
        self.assertEqual(self.singleton.avg_mood_today, 10.0)
        self.assertEqual(self.singleton.sign_today, "+")

    def test_pulse_sign_logic(self):
        """Verify the pulse sign logic based on sentiment dominancy."""
        # Dominant Happy: (+)
        self.Check.create(
            {"mood_score": 10, "sentiment": "happy", "date": fields.Date.today()}
        )
        self.singleton._refresh_pulse()
        self.assertEqual(self.singleton.sign_today, "+")

        # Dominant Sad: (-)
        self.Check.create(
            {"mood_score": 2, "sentiment": "sad", "date": fields.Date.today()}
        )
        self.Check.create(
            {"mood_score": 2, "sentiment": "sad", "date": fields.Date.today()}
        )
        self.singleton._refresh_pulse()
        self.assertEqual(self.singleton.sign_today, "-")
