# Copyright (C) 2015 Salton Massally (<smassally@idtlabs.sl>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    age = fields.Integer(
        string='Age',
        readonly=True,
        compute='_compute_age',
    )

    @api.multi
    @api.depends('birthday')
    def _compute_age(self):
        for record in self:
            age = 0
            if record.birthday:
                age = relativedelta(
                    fields.Date.from_string(fields.Date.today()),
                    fields.Date.from_string(record.birthday)).years
            record.age = age
