from odoo.tests.common import TransactionCase
from odoo import fields


class TestWellnessWizard(TransactionCase):
    def setUp(self):
        super(TestWellnessWizard, self).setUp()
        self.Wizard = self.env["wellness.check.wizard"]
        self.Check = self.env["wellness.check"]
        self.User = self.env.user

        # Setup test questions
        self.env["wellness.question"].create(
            [
                {"name": "Q1", "sequence": 1},
                {"name": "Q2", "sequence": 2},
                {"name": "Q3", "sequence": 3},
            ]
        )

    def test_wizard_default_get(self):
        """Verify that wizard correctly loads question labels."""
        wizard = self.Wizard.create({})
        self.assertEqual(wizard.q1_label, "Q1")
        self.assertEqual(wizard.q2_label, "Q2")
        self.assertEqual(wizard.q3_label, "Q3")

    def test_wizard_action_submit(self):
        """Verify that submitting the wizard creates a record and updates user."""
        wizard = self.Wizard.create(
            {
                "mood_score": 10,
                "q1_answer": "I am happy",
                "q2_answer": "Lunch was good",
                "q3_answer": "No suggestions",
            }
        )

        action = wizard.action_submit()
        self.assertEqual(action["type"], "ir.actions.act_window_close")

        # One check should be created
        check = self.Check.search([], limit=1, order="id desc")
        self.assertEqual(check.mood_score, 10)
        self.assertEqual(check.q1_answer, "I am happy")
        self.assertEqual(check.sentiment, "happy")

        # User should be updated to today
        self.assertEqual(self.User.last_hr_wellness_check_date, fields.Date.today())

    def test_wizard_action_skip(self):
        """Verify that skipping updates user but creates no record."""
        count_before = self.Check.search_count([])
        wizard = self.Wizard.create({})

        action = wizard.action_skip()
        self.assertEqual(action["type"], "ir.actions.act_window_close")

        # No check should be created
        self.assertEqual(self.Check.search_count([]), count_before)

        # User should still be updated
        self.assertEqual(self.User.last_hr_wellness_check_date, fields.Date.today())
