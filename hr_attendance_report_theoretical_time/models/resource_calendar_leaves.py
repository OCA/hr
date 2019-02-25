from odoo import api, models


class ResourceCalendarLeaves(models.Model):
    _inherit = 'resource.calendar.leaves'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """
        Inject extra domain when being called from _theoretical_hours method.
        WARNING: This method should be called only once with that context
        from a restricted piece of code, or can have side effects.
        """
        if self.env.context.get('leave_holiday_domain'):
            args += self.env.context.get('leave_holiday_domain')
        return super(ResourceCalendarLeaves, self).search(
            args, offset=offset, limit=limit, order=order, count=count)
