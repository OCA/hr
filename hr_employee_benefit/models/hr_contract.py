from odoo import fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    benefit_line_ids = fields.One2many(
        comodel_name='hr.employee.benefit',
        inverse_name='contract_id',
        string='Employee Benefits',
    )
