from odoo import api, fields, models

class ResUsers(models.Model):
    """ 
    Extension of res.users to manage login-based wellness prompts.
    
    The system tracks the date of the last wellness check completed 
    by each user. This ensures that employees are not prompted more 
    than once per calendar day. 
    """
    _inherit = 'res.users'

    last_hr_wellness_check_date = fields.Date(
        string='Last Wellness Check Date',
        help="The most recent date the user completed a sentiment check. Used to throttle daily popups."
    )

    @api.model
    def check_wellness_prompt(self):
        """ 
        Frontend Trigger Logic.
        
        Called by the JavaScript bridge during the Odoo web client boot sequence.
        Returns True if:
        1. The user is logged in (not a public/portal user).
        2. The user has not yet completed a check today.
        """
        # Exclude bot users and unauthorized users
        if self.env.user.id == self.env.ref('base.public_user').id:
            return False
            
        today = fields.Date.context_today(self)
        
        # Check if the prompt is required for the current session
        if not self.env.user.last_hr_wellness_check_date or self.env.user.last_hr_wellness_check_date < today:
            return True
            
        return False
