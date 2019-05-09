from odoo import api, fields, models, _
from odoo.exceptions import UserError


class DutyShiftReport(models.AbstractModel):
    _name = 'report.hr_duty_shift.report_duty_shift'

    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_(
                "Form content is missing, this report cannot be printed."))

        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        shifts = self.env['hr.duty.shift'].search(
            [('start_date', '>=', date_from), ('start_date', '<=', date_to)]
        )

        values = {}
        for shift in shifts:
            employee_id = shift.employee_id.id
            start_date = fields.Datetime.from_string(shift.start_date)
            end_date = fields.Datetime.from_string(shift.end_date)

            if employee_id not in values:
                values[employee_id] = [shift.employee_id.name, 0.0, 0.0]
            delta_time = (end_date - start_date).total_seconds() / 3600.0

            values[employee_id][1] += delta_time
            if shift.is_paid:
                values[employee_id][2] += delta_time

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_from': date_from,
            'date_to': date_to,
            'values': sorted(values.values(), key=lambda r: r[0]),
        }
