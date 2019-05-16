# copyright 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployee(models.Model):
    """Enhance the features of the employee using Number details."""

    _inherit = 'hr.employee'

    internal_number = fields.Char('Internal Number',
                                  help='Internal phone number.')
    short_number = fields.Char('Short Number',
                               help='Short phone number.')
