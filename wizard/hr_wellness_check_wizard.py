from odoo import api, fields, models

class WellnessCheckWizard(models.Model):
    """ 
    Daily Wellness Pulse Check Wizard.
    
    This transient model provides the user interface for the daily popup.
    It dynamically pulls active questions from the wellness.question model 
    and presents them to the employee.
    
    Data Privacy: After the survey is submitted, the logic creates a 
    disconnected 'wellness.check' record to ensure anonymity.
    """
    _name = 'wellness.check.wizard'
    _description = 'Wellness Check Wizard'

    def _default_questions(self):
        """ Fetch the top 3 active questions sorted by sequence. """
        questions = self.env['wellness.question'].search([('active', '=', True)], limit=3, order='sequence, id')
        return questions

    # Labels populated dynamically during default_get
    q1_label = fields.Char()
    q2_label = fields.Char()
    q3_label = fields.Char()

    mood_score = fields.Integer(
        string='On a scale of 1 to 10, how are you today?', 
        default=5,
        help="Main numerical sentiment metric (1-10)."
    )
    
    q1_answer = fields.Text(string='Answer 1')
    q2_answer = fields.Text(string='Answer 2')
    q3_answer = fields.Text(string='Answer 3')

    @api.model
    def default_get(self, fields_list):
        res = super(WellnessCheckWizard, self).default_get(fields_list)
        questions = self._default_questions()
        
        if len(questions) > 0:
            res['q1_label'] = questions[0].name
        else:
            res['q1_label'] = 'How are you today?'
            
        if len(questions) > 1:
            res['q2_label'] = questions[1].name
        else:
            res['q2_label'] = 'What was the highlight of your day?'
            
        if len(questions) > 2:
            res['q3_label'] = questions[2].name
        else:
            res['q3_label'] = 'Any suggestions for morale improvement?'
            
        return res

    def action_submit(self):
        """ 
        Submits the survey and ensures anonymity.
        1. Creates a disconnected wellness.check record.
        2. Marks the user's login date to prevent multiple prompts today.
        """
        self.env['wellness.check'].create({
            'q1_answer': self.q1_answer,
            'q2_answer': self.q2_answer,
            'q3_answer': self.q3_answer,
            'mood_score': self.mood_score or 5,
        })
        # Record completion to stop daily popups
        self.env.user.last_hr_wellness_check_date = fields.Date.context_today(self)
        return {'type': 'ir.actions.act_window_close'}

    def action_skip(self):
        """ 
        Dismisses the survey for the current day. 
        Marks the day as 'checked' but does not create a sentiment record.
        """
        self.env.user.last_hr_wellness_check_date = fields.Date.context_today(self)
        return {'type': 'ir.actions.act_window_close'}
