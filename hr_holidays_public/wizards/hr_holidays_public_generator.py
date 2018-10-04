# Copyright 2018 elego Software Solutions GmbH - Yu Weng
# Copyright 2018 initOS GmbH - Nikolina Todorova
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError

COUNTRY_GENERATORS = []


class HrHolidaysPublicGenerator(models.TransientModel):
    """
    Usage:
    * generate public holidays for specific country (if there
        is no template set)
    * copy public holidays for specific country
    To extend the model one should:
    * create new module with name "hr_holidays_public_generator_<country code>"
    * create wizard that inherit "hr.holidays.public.generator"
    * implement copy public holidays function with name action_copy_%s_holidays
        where %s id the county code
    * implement generate public holidays function with
        name action_generate_%s_holidays where %s id the county code
    """
    _name = 'hr.holidays.public.generator'

    year = \
        fields.Integer(
            'Year',
            required=True,
            default=(lambda self: datetime.today().year)
        )
    country_id = \
        fields.Many2one(
            'res.country',
            string='Country',
            required=True,
            domain=[('code', 'in', COUNTRY_GENERATORS)])
    state_id = fields.Many2one('res.country.state', string='State')
    template_id = \
        fields.Many2one('hr.holidays.public', string='From Template')

    @api.onchange('template_id')
    def onchange_template_id(self):
        if self.template_id:
            self.country_id = \
                self.template_id.country_id and \
                self.template_id.country_id.id or \
                False

    @api.multi
    def generate_function_copy_name(self):
        function_name = \
            'action_copy_%s_holidays' % self.country_id.code.lower()
        return function_name

    @api.multi
    def generate_function_generate_name(self):
        function_name = \
            'action_generate_%s_holidays' % self.country_id.code.lower()
        return function_name

    @api.multi
    def action_run(self):
        self.ensure_one()
        if self.template_id:
            function_name = self.generate_function_copy_name()
            if not hasattr(self, function_name):
                raise UserError(_(
                    """There is no copy function defined for this county or
                    the function name does not fit the requirement -
                    action_copy_%s_holidays where %s id the county code."""
                ))
            getattr(self, function_name)()
        else:
            function_name = self.generate_function_generate_name()
            if not hasattr(self, function_name):
                raise UserError(_(
                    """There is no generate function defined for this county
                    or the function name does not fit the requirement -
                    action_generate_%s_holidays where %s is
                    the county code."""
                ))
            getattr(self, function_name)()
