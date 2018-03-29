# -*- coding: utf-8 -*-
# © 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    infraction_ids = fields.One2many(
        comodel_name='hr.infraction',
        inverse_name='employee_id',
        string='Infractions',
        readonly=True,
    )
