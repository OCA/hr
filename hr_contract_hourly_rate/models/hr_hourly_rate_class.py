# Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from itertools import permutations


class HrHourlyRateClass(models.Model):
    _name = 'hr.hourly.rate.class'
    _description = 'Hourly rate class'

    name = fields.Char(string='Class Name', required=True, index=True)
    line_ids = fields.One2many('hr.hourly.rate',
                               'class_id',
                               string='Hourly Rates')
    contract_job_ids = fields.One2many('hr.contract.job',
                                       'hourly_rate_class_id',
                                       string='Contract Jobs')

    @api.constrains('line_ids')
    def _check_overlapping_rates(self):
        """
        Checks if a class has two rates that overlap in time.
        """
        for hourly_rate_class in self:
            for r1, r2 in permutations(hourly_rate_class.line_ids, 2):
                if (r1.date_end and (
                        r1.date_start <= r2.date_start <= r1.date_end
                )) or (not r1.date_end and (r1.date_start <= r2.date_start)):
                    raise ValidationError(
                        _("Error! You cannot have overlapping rates"))
        return True
