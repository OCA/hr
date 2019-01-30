from odoo import api, fields, models


class Attendance(models.Model):
    _inherit = 'hr.attendance'

    real_check_in = fields.Datetime(required=True)
    real_check_out = fields.Datetime()
    needs_approval = fields.Boolean()

    @api.model_cr_context
    def _init_column(self, column_name):
        # Set a value on existing data for required fields
        if column_name == 'real_check_in':
            self.env.cr.execute("UPDATE hr_attendance SET real_check_in = check_in WHERE real_check_in IS NULL")
        elif column_name == 'real_check_out':
            self.env.cr.execute("UPDATE hr_attendance SET real_check_out = check_out WHERE real_check_out IS NULL")
        super()._init_column(column_name)
