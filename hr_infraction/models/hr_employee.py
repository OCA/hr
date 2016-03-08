from openerp import models, fields


class HrEmployee(models.Model):

    _name = 'hr.employee'
    _inherit = 'hr.employee'
    infraction_ids = fields.One2many(
        comodel_name='hr.infraction',
        inverse_name='employee_id',
        string='Infractions',
        readonly=True,
    )
