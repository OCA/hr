# Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models, fields


class HrHourlyRate(models.Model):
    _name = 'hr.hourly.rate'
    _description = 'Hourly rate'

    rate = fields.Float(string='Rate', required=True)
    date_start = fields.Date(string='Start Date', required=True,
                             default=fields.Date.today())
    date_end = fields.Date(string='End Date')
    class_id = fields.Many2one('hr.hourly.rate.class',
                               string='Salary Class',
                               ondelete='cascade',
                               required=True)
