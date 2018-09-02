# ©  2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
# ©  2014 initOS GmbH & Co. KG <http://www.initos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrHolidaysPublicLine(models.Model):
    _name = 'hr.holidays.public.line'
    _description = 'Public Holidays Lines'
    _order = "date, name desc"

    name = fields.Char(
        'Name',
        required=True,
    )
    date = fields.Date(
        'Date',
        required=True
    )
    year_id = fields.Many2one(
        'hr.holidays.public',
        'Calendar Year',
        required=True,
    )
    variable_date = fields.Boolean('Date may change', oldname='variable',
                                   default=True)
    state_ids = fields.Many2many(
        'res.country.state',
        'hr_holiday_public_state_rel',
        'line_id',
        'state_id',
        'Related States'
    )
    calendar_leave_id = fields.Many2one(
        'resource.calendar.leaves',
        'Resource Calendar Leave', copy=False)

    @api.multi
    @api.constrains('date', 'state_ids')
    def _check_date_state(self):
        for line in self:
            line._check_date_state_one()

    def _check_date_state_one(self):
        if fields.Date.from_string(self.date).year != self.year_id.year:
            raise UserError(_(
                'Dates of holidays should be the same year '
                'as the calendar year they are being assigned to'
            ))

        if self.state_ids:
            domain = [('date', '=', self.date),
                      ('year_id', '=', self.year_id.id),
                      ('state_ids', '!=', False),
                      ('id', '!=', self.id)]
            holidays = self.search(domain)

            for holiday in holidays:

                if self.state_ids & holiday.state_ids:
                    raise UserError(_('You can\'t create duplicate public '
                                      'holiday per date %s and one of the '
                                      'country states.') % self.date)
        domain = [('date', '=', self.date),
                  ('year_id', '=', self.year_id.id),
                  ('state_ids', '=', False)]
        if self.search_count(domain) > 1:
            raise UserError(_('You can\'t create duplicate public holiday '
                              'per date %s.') % self.date)
        return True
