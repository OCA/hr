from odoo import fields, models


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    def get_action_date(self, in_out, employee_id):
        results = (a.get_action_date(in_out, employee_id) for a in self.attendance_ids)
        return next(((d, a) for d, a in results if d is not None), (fields.Datetime.now(), True))
