# © 2015 Salton Massally <smassally@idtlabs.sl>
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HumanResourcesConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'hr.employeeid.config.settings'

    def _default_id_gen_method(self):
        gen_method = self.env.user.company_id.employee_id_gen_method
        if not gen_method:
            gen_method = self.env['res.company'].default_get(
                ['employee_id_gen_method']
            )['employee_id_gen_method']
        return gen_method

    def _default_id_random_digits(self):
        digits = self.env.user.company_id.employee_id_random_digits
        if not digits:
            digits = self.env['res.company'].default_get(
                ['employee_id_random_digits']
            )['employee_id_random_digits']
        return digits

    def _default_id_sequence(self):
        sequence = self.env.user.company_id.employee_id_sequence
        if not sequence:
            sequence = self.env.ref('hr_employee_id.seq_employeeid_ref')
        return sequence and sequence.id or False

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.user.company_id)

    employee_id_gen_method = fields.Selection(
        related='company_id.employee_id_gen_method',
        default=_default_id_gen_method
    )
    employee_id_random_digits = fields.Integer(
        related='company_id.employee_id_random_digits',
        default=_default_id_random_digits
    )
    employee_id_sequence = fields.Many2one(
        'ir.sequence',
        related='company_id.employee_id_sequence',
        default=_default_id_sequence
    )
