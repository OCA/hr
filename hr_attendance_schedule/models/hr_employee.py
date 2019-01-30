from odoo import api, exceptions, fields, models, _


class Employee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def attendance_action_change(self):  #pragma: no cover
        """ Check In/Check Out action
            Check In: create a new attendance record
            Check Out: modify check_out field of appropriate attendance record
        """
        if len(self) > 1:
            raise exceptions.UserError(_('Cannot perform check in or check out on multiple employees.'))
        action_date, needs_approval = self._get_action_date()

        if self.attendance_state != 'checked_in':
            vals = {
                'employee_id': self.id,
                'check_in': action_date,
                'real_check_in': fields.Datetime.now(),
                'needs_approval': needs_approval
            }
            return self.env['hr.attendance'].create(vals)
        else:
            attendance = self.env['hr.attendance'].search([('employee_id', '=', self.id), ('check_out', '=', False)], limit=1)
            if attendance:
                attendance.write({
                    'check_out': action_date,
                    'real_check_out': fields.Datetime.now(),
                    'needs_approval': needs_approval
                })
            else:
                raise exceptions.UserError(_('Cannot perform check out on %(empl_name)s, could not find corresponding check in. '
                    'Your attendances have probably been modified manually by human resources.') % {'empl_name': self.name, })
            return attendance

    def _get_action_date(self):
        in_out = 'out' if self.attendance_state == 'checked_in' else 'in'
        return self.resource_calendar_id.get_action_date(in_out, self)
