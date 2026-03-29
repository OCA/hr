from odoo.tests.common import TransactionCase
from odoo import fields


class TestWellnessCheck(TransactionCase):
    def setUp(self):
        super(TestWellnessCheck, self).setUp()
        self.User = self.env["res.users"]
        self.Check = self.env["wellness.check"]

        # Use an existing internal user or create one
        self.test_user = self.User.create(
            {
                "name": "Test Wellness User",
                "login": "test_wellness_user",
                "email": "test@wellness.com",
                "groups_id": [(4, self.env.ref("base.group_user").id)],
            }
        )

    def test_sentiment_calculation(self):
        """Test that sentiment is correctly calculated based on mood score."""
        # Happy: 8-10
        check_happy = self.Check.create({"mood_score": 9})
        self.assertEqual(check_happy.sentiment, "happy")

        # Neutral: 5-7
        check_neutral = self.Check.create({"mood_score": 6})
        self.assertEqual(check_neutral.sentiment, "neutral")

        # Sad: 1-4
        check_sad = self.Check.create({"mood_score": 3})
        self.assertEqual(check_sad.sentiment, "sad")

    def test_user_prompt_logic(self):
        """Test the logic that determines if a user should see the prompt."""
        # Initially, the user should be prompted
        self.assertTrue(
            self.test_user.with_user(self.test_user).check_wellness_prompt()
        )

        # After completing a check
        self.test_user.last_hr_wellness_check_date = fields.Date.today()
        self.assertFalse(
            self.test_user.with_user(self.test_user).check_wellness_prompt()
        )

        # On a new day, they should be prompted again
        self.test_user.last_hr_wellness_check_date = fields.Date.subtract(
            fields.Date.today(), days=1
        )
        self.assertTrue(
            self.test_user.with_user(self.test_user).check_wellness_prompt()
        )

    def test_sentiment_edge_cases(self):
        """Test with empty answers and mixed signals."""
        # Empty answers should remain neutral if mood is 5
        check_empty = self.Check.create({"mood_score": 5})
        self.assertEqual(check_empty.sentiment, "neutral")

        # High mood but negative keywords (mood should win at 9)
        check_mixed = self.Check.create(
            {"mood_score": 9, "q1_answer": "stressed and tired"}
        )
        self.assertEqual(check_mixed.sentiment, "happy")

    def test_post_init_hook(self):
        """Verify the module post_init_hook runs without error."""
        from .. import post_init_hook

        # This should call refresh_pulse on the dashboard
        post_init_hook(self.env)

    def test_questionnaire_ordering(self):
        """Test the sequence ordering of wellness questions."""
        Quest = self.env["wellness.question"]
        Quest.create({"name": "Rare Question", "sequence": 999})
        Quest.create({"name": "First Question", "sequence": 1})

        ordered = Quest.search([], limit=1)
        self.assertEqual(ordered.name, "First Question")
