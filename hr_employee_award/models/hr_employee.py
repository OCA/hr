# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    award_ids = fields.One2many(
        string='Awards',
        comodel_name='hr.award',
        inverse_name='employee_id',
        readonly=False,
        )
