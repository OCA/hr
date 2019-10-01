from datetime import timedelta
from odoo import api, fields, models, SUPERUSER_ID


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    mute_warnings = fields.Boolean(string='Mute Warnings')

    def get_warning_domain(self, date):
        today = fields.Datetime.from_string(date)
        tomorrow = today + timedelta(days=1)
        today = fields.Datetime.to_string(today)
        tomorrow = fields.Datetime.to_string(tomorrow)
        return [('create_date', '>=', today),
                ('create_date', '<', tomorrow),
                ('employee_id', '=', self.id)]

    def _create_warning(self, w_type, date, min_int=False, max_int=False):
        if not self.active or self.mute_warnings:
            return
        warning_obj = self.env['hr.attendance.warning']
        warning = warning_obj.search(self.get_warning_domain(date), limit=1)
        if warning:
            warning.sudo(user=SUPERUSER_ID).write({
                'state': 'pending',
                'warning_line_ids': [(0, 0, {
                    'warning_type': w_type,
                    'min_int': min_int,
                    'max_int': max_int,
                })]
            })
        else:
            self.env['hr.attendance.warning'].sudo(user=SUPERUSER_ID).create(
                self._create_warning_vals(w_type, min_int, max_int)
            )
        warning_obj.update_counter()

    def _create_warning_vals(self, w_type, min_int=False, max_int=False):
        return {
            'employee_id': self.id,
            'warning_line_ids': [(0, 0, {
                'warning_type': w_type,
                'min_int': min_int,
                'max_int': max_int,
            })]
        }

    @api.multi
    def attendance_action_change(self):
        attendance = super(HrEmployee, self).attendance_action_change()
        if attendance:
            action_time = fields.Datetime.from_string(
                attendance.check_out or attendance.check_in
            )

            in_interval = any([
                att[0] + timedelta(
                    minutes=-att.data['attendances'].margin_from or 0
                ) <= action_time <= att[1] + timedelta(
                    minutes=att.data['attendances'].margin_to or 0
                )
                for att in self.resource_calendar_id._get_day_work_intervals(
                    action_time.date(),
                    start_time=False,
                    end_time=False,
                    compute_leaves=True,
                    resource_id=self.resource_id.id
                )])

            public_holiday = self.env['hr.holidays.public'].is_public_holiday(
                action_time.date(), self.id
            )

            if not in_interval or public_holiday:
                date = fields.Date.to_string(action_time.date())
                # TODO: Is this warning really necessary?
                # self._create_warning(date=date, w_type='out_of_interval')
        return attendance
