# -*- coding: utf-8 -*-
# © 2011 Michael Telahun Makonnen <mmakonnen@gmail.com>
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    emergency_contact_ids = fields.Many2many(
        string='Emergency Contacts',
        comodel_name='res.partner',
        relation='rel_employee_emergency_contact',
        column1='employee_id',
        column2='partner_id',
        domain=[
            ('is_company', '=', False),
            ]
        )
