# Copyright 2015 Savoir-faire Linux. All Rights Reserved.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    contract_id = fields.Many2one(search='_search_contract')

    @api.model
    def _search_contract(self, operator, value):
        res = []
        contract_ids = self.env['hr.contract'].search(
            [('employee_id', operator, value)])
        res.append(('id', 'in', contract_ids.ids))
        return res
