# -*- coding: utf-8 -*-
# © 2015 Salton Massally <smassally@idtlabs.sl>
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class HumanResourcesConfiguration(models.TransientModel):
    _inherit = 'hr.config.settings'

    def _default_id_sequence(self):
        sequence = self.env.ref('hr_employee_id.seq_employeeid_ref')
        return sequence and sequence.id or False

    employee_id_gen_method = fields.Selection(
        selection=[
            ('random', 'Random'),
            ('sequence', 'Sequence'),
        ],
        string="ID Generation Method",
        default='random'
    )
    employee_id_random_digits = fields.Integer(
        string='# of Digits',
        default=5,
        help="Number of digits making up the ID"
    )
    employee_id_sequence = fields.Many2one(
        comodel_name='ir.sequence',
        string='Sequence',
        help="Pattern to be used for used for ID Generation",
        default=_default_id_sequence
    )

    @api.model
    def get_default_employee_id_values(self, fields):
        company = self.env.user.company_id
        return {
            'employee_id_gen_method': company.employee_id_gen_method,
            'employee_id_random_digits': company.employee_id_random_digits,
            'employee_id_sequence': company.employee_id_sequence.id,
        }

    @api.one
    def set_employee_id_values(self):
        company = self.env.user.company_id
        company.employee_id_gen_method = self.employee_id_gen_method
        company.employee_id_random_digits = self.employee_id_random_digits
        company.employee_id_sequence = self.employee_id_sequence

    @api.onchange('employee_id_gen_method')
    def onchange_employee_id_gen_method(self):
        if self.employee_id_gen_method == 'sequence':
            self.employee_id_sequence = self._default_id_sequence()
