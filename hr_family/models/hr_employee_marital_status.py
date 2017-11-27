# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class HrEmployeeMaritalStatus(models.Model):
    _name = 'hr.employee.marital.status'
    _description = 'Marital status'

    name = fields.Char(required=True, translate=True)
    code = fields.Char()

    @api.multi
    def name_get(self):
        return [
            (
                this.id,
                '[%s] %s' % (this.code, this.name) if this.code
                else this.name
            )
            for this in self
        ]
