import datetime

from odoo import api, fields, models

class WellnessCheck(models.Model):
    """ 
    Anonymous Wellness Check-in Record.
    
    This model stores daily sentiment feedback from employees. To maintain 
    strict anonymity, this model is deliberately NOT linked to the res.users 
    or hr.employee models via Many2one fields.
    
    The records are processed using a simple keyword-based sentiment engine 
    to provide HR with aggregate insights into workplace morale.
    """
    _name = 'wellness.check'
    _description = 'Anonymous Wellness Check-in'
    _order = 'date desc'

    date = fields.Date(
        string='Date', 
        default=fields.Date.context_today, 
        readonly=True,
        help="The date when the pulse check was completed."
    )
    
    # Answers to the daily survey (referenced from wellness.question titles)
    q1_answer = fields.Text(string='Answer 1')
    q2_answer = fields.Text(string='Answer 2')
    q3_answer = fields.Text(string='Answer 3')
    
    mood_score = fields.Integer(
        string='Mood Score (1-10)', 
        default=5,
        aggregator="avg",
        help="Self-reported numerical mood score from 1 (lowest) to 10 (highest)."
    )
    
    sentiment = fields.Selection([
        ('happy', 'Happy'),
        ('neutral', 'Neutral'),
        ('sad', 'Sad')
    ], string='Sentiment', compute='_compute_sentiment', store=True,
       help="Categorization of the employee's morale based on mood and keywords.")
       
    analysis = fields.Text(
        string='Automated Analysis', 
        compute='_compute_sentiment', 
        store=True,
        help="Summarized interpretation of the employee's feedback."
    )

    @api.depends('q1_answer', 'q2_answer', 'q3_answer', 'mood_score')
    def _compute_sentiment(self):
        """ 
        Scoring Engine: Analyzes text answers for positive/negative keywords 
        and combines the result with the reported mood score to determine 
        the overall sentiment level ('happy', 'neutral', 'sad').
        """
        # Keyword dictionaries for basic NLP analysis
        positive_keywords = ['happy', 'great', 'good', 'excellent', 'love', 'nice', 'smooth', 'efficient', 'motivated', 'well', 'fine', 'thanks', 'cool', 'perfect', 'awesome', 'excited', 'progress', 'team', 'help', 'happy']
        negative_keywords = ['sad', 'bad', 'poor', 'stress', 'tired', 'burnt', 'hard', 'difficult', 'noise', 'annoying', 'busy', 'pressure', 'broken', 'wait', 'slow', 'boring', 'angry', 'unhappy', 'lonely', 'stressful', 'exhausted']

        for record in self:
            # Aggregate all answers for cross-question keyword search
            text = f"{(record.q1_answer or '')} {(record.q2_answer or '')} {(record.q3_answer or '')}".lower()
            
            # Simple keyword frequency calculation
            pos_count = sum(1 for word in positive_keywords if word in text)
            neg_count = sum(1 for word in negative_keywords if word in text)
            
            score = pos_count - neg_count
            
            # Hybrid Sentiment Logic: 
            # Prioritizes high/low mood scores but allows keywords to shift a neutral score.
            if record.mood_score >= 8 or (score > 1 and record.mood_score >= 6):
                record.sentiment = 'happy'
            elif record.mood_score <= 4 or (score < -1 and record.mood_score <= 5):
                record.sentiment = 'sad'
            else:
                record.sentiment = 'neutral'
                
            # Content Generation: Explain the data behind the classification
            summary = ""
            if record.sentiment == 'happy':
                summary = "Employee seems to be in good spirits. "
                if pos_count > 0:
                    summary += f"Positive keywords detected ({pos_count})."
            elif record.sentiment == 'sad':
                summary = "Employee feedback shows lower morale. "
                if neg_count > 0:
                    summary += f"Negative keywords detected ({neg_count})."
            else:
                summary = "Employee has a neutral sentiment."
            
            record.analysis = summary

    @api.model
    def get_wellness_stats(self):
        """ 
        Computed KPIs for the Odoo Management Dashboard.
        
        Calculates:
        - Participation Today: Count of checks received today.
        - Avg Mood Score Today: Continuous metric for current daily morale.
        - 3-Day Trend: Qualitative assessment comparing recent avg vs previous period.
        
        Returns a dictionary for the OWL dashboard component.
        """
        today = fields.Date.today()
        three_days_ago = today - datetime.timedelta(days=3)
        six_days_ago = today - datetime.timedelta(days=6)

        # Calculate participation metrics
        today_records = self.search([('date', '=', today)])
        participation_today = len(today_records)

        # Average mood calculation
        avg_mood_today = sum(today_records.mapped('mood_score')) / participation_today if participation_today > 0 else 0

        # Sign of the day: + if happy > sad, - if sad > happy
        happy_count = len(today_records.filtered(lambda r: r.sentiment == 'happy'))
        sad_count = len(today_records.filtered(lambda r: r.sentiment == 'sad'))
        
        sign = "stable"
        if happy_count > sad_count:
            sign = "+"
        elif sad_count > happy_count:
            sign = "-"
        else:
            sign = "="

        # Trend analysis logic
        last_3_days = self.search([('date', '>', three_days_ago), ('date', '<=', today)])
        prev_3_days = self.search([('date', '>', six_days_ago), ('date', '<=', three_days_ago)])

        last_avg = sum(last_3_days.mapped('mood_score')) / len(last_3_days) if last_3_days else 0
        prev_avg = sum(prev_3_days.mapped('mood_score')) / len(prev_3_days) if prev_3_days else 0

        trend = "stable"
        if last_avg > prev_avg + 0.5:
            trend = "up"
        elif last_avg < prev_avg - 0.5:
            trend = "down"

        return {
            'participation_today': participation_today,
            'avg_mood_today': round(avg_mood_today, 1),
            'trend': trend,
            'sign': sign,
            'trend_label': f"{'+' if last_avg >= prev_avg else ''}{round(last_avg - prev_avg, 1)} pts"
        }
