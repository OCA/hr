# Copyright (C) 2015 Salton Massally.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    age = fields.Integer(
        string='Age',
        compute='_compute_age'
    )

    @api.multi
    @api.depends('birthday')
    def _compute_age(self):
        for record in self:
            if record.birthday:
                today = fields.Date.today()
                if record.birthday > today:
                    raise Warning(
                        _("You can not set birthday grater than today.!!"))
                record.age = relativedelta(
                    fields.Date.from_string(today),
                    fields.Date.from_string(record.birthday)).years
            else:
                record.age = 0
