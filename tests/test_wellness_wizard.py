from odoo.tests.common import TransactionCase
from odoo import fields

class TestWellnessWizard(TransactionCase):

    def setUp(self):
        super(TestWellnessWizard, self).setUp()
        self.Wizard = self.env['wellness.check.wizard']
        self.Check = self.env['wellness.check']
        
        # Clear existing data to ensure deterministic results
        self.env['wellness.question'].search([]).unlink()
        self.Check.search([]).unlink()
        
        # Ensure we have active questions for default_get tests
        self.question_1 = self.env['wellness.question'].create({
            'name': 'How is your work-life balance?',
            'active': True,
            'sequence': 1,
        })
        self.question_2 = self.env['wellness.question'].create({
            'name': 'Are you happy with your tools?',
            'active': True,
            'sequence': 2,
        })

    def test_wizard_default_get_labels(self):
        """Verify the wizard pulls correct active questions into labels."""
        res = self.Wizard.default_get(['q1_label', 'q2_label', 'q3_label'])
        
        self.assertEqual(res.get('q1_label'), 'How is your work-life balance?')
        self.assertEqual(res.get('q2_label'), 'Are you happy with your tools?')
        # The 3rd should be a default fallback since we only created 2
        self.assertEqual(res.get('q3_label'), 'Any suggestions for morale improvement?')

    def test_wizard_submission(self):
        """Test that submitting the wizard creates an anonymous check record."""
        # Create wizard instance
        wizard = self.Wizard.create({
            'mood_score': 10,
            'q1_answer': 'Perfect balance!',
            'q2_answer': 'Yes, very much.',
        })
        
        # Submit the wizard
        wizard.action_submit()
        
        # Verify the created record content
        check = self.Check.search([], order='id desc', limit=1)
        self.assertEqual(check.mood_score, 10)
        self.assertEqual(check.sentiment, 'happy')
        self.assertEqual(check.q1_answer, 'Perfect balance!')
        
        # Verify the user's completion status is updated.
        self.assertEqual(self.env.user.last_hr_wellness_check_date, fields.Date.today())
