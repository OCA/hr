# copyright 2011 Michael Telahun Makonnen <mmakonnen@gmail.com>
# copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    emergency_contact_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Emergency Contacts',
        relation='rel_employee_emergency_contact',
        domain=[
            ('is_company', '=', False),
        ]
    )
