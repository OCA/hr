# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WizardDutyShiftReport(models.TransientModel):

    _name = 'wizard.duty_shift.report'

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    @api.multi
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': self.ids,
            'model': self._name,
            'form': data
        }
        return self.env.ref(
            'hr_duty_shift.action_report_duty_shift'
        ).report_action(self, data=datas)

    @api.constrains('date_from', 'date_to')
    def check_date(self):
        for record in self:
            if (record.date_from and record.date_to and
                    record.date_from > record.date_to):
                raise ValidationError(
                    _('The start date must be anterior to the end date.')
                )
