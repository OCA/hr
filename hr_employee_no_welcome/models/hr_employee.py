# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    @api.model
    def create(self, vals):
        return super(
            HrEmployee, self.with_context(mail_broadcast=False)).create(vals)
