# Copyright 2018 elego Software Solutions GmbH - Yu Weng
# Copyright 2018 initOS GmbH - Nikolina Todorova
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.addons.hr_holidays_public_generator.wizard.hr_holidays_public_generator import \
    COUNTRY_GENERATORS
from odoo.exceptions import UserError

COUNTRY_GENERATORS.append("DE")


class HrHolidaysPublicGenerator(models.TransientModel):
    _inherit = 'hr.holidays.public.generator'

    @api.model
    def calculate_easter_sunday(self, year):
        d = (((255 - 11 * (year % 19)) - 21) % 30) + 21
        if d > 48:
            d += 1
        delta = d + 6 - ((year + (year - (year % 4)) // 4) + d + 1) % 7
        str_3_1 = '%s-03-01' % year
        date_3_1 = fields.Datetime.from_string(str_3_1)
        easter = date_3_1 + timedelta(days=delta)
        return easter

    @api.model
    def calculate_new_good_friday(self, easter):
        good_friday = easter - timedelta(days=2)
        return fields.Date.to_string(good_friday)

    @api.model
    def calculate_easter_monday(self, easter):
        easter_monday = easter + timedelta(days=1)
        return fields.Date.to_string(easter_monday)

    @api.model
    def calculate_ascension_day(self, easter):
        ascension_day = easter + timedelta(days=39)
        return fields.Date.to_string(ascension_day)

    @api.model
    def calculate_whit_monday(self, easter):
        whit_monday = easter + timedelta(days=50)
        return fields.Date.to_string(whit_monday)

    @api.model
    def calculate_corpus_christi(self, easter):
        corpus_christi = easter + timedelta(days=60)
        return fields.Date.to_string(corpus_christi)

    @api.model
    def calculate_floating_holidays(self, existing_holidays):
        public_holiday_line_obj = self.env['hr.holidays.public.line']
        easter = self.calculate_easter_sunday(self.year)

        public_holiday_line_obj.create({'name': _('Good Friday'),
                                        'date':
                                            self.calculate_new_good_friday(
                                                easter),
                                        'variable_date': True,
                                        'year_id': existing_holidays.id})
        public_holiday_line_obj.create({'name': _('Easter Sunday'),
                                        'date': fields.Date.to_string(easter),
                                        'variable_date': True,
                                        'year_id': existing_holidays.id})

        public_holiday_line_obj.create({'name': _('Easter Monday'),
                                        'date':
                                            self.calculate_easter_monday(
                                                easter),
                                        'variable_date': True,
                                        'year_id': existing_holidays.id})
        public_holiday_line_obj.create({'name': _('Ascension Day'),
                                        'date':
                                            self.calculate_ascension_day(
                                                easter),
                                        'variable_date': True,
                                        'year_id': existing_holidays.id})

        public_holiday_line_obj.create({'name': _('Whit Monday'),
                                        'date':
                                            self.calculate_whit_monday(
                                                easter),
                                        'variable_date': True,
                                        'year_id': existing_holidays.id})

    @api.model
    def calculate_state_floating_holidays(self,
                                          existing_holidays,
                                          state=None):
        public_holiday_line_obj = self.env['hr.holidays.public.line']
        easter = self.calculate_easter_sunday(self.year)
        # Baden-Württemberg, Bavaria, Hesse, North
        # Rhine-Westphalia, Rhineland-Palatinate, Saarland
        state_ids = [
            self.env.ref('l10n_de_country_states.res_country_state_BW').id,
            self.env.ref('l10n_de_country_states.res_country_state_BY').id,
            self.env.ref('l10n_de_country_states.res_country_state_HE').id,
            self.env.ref('l10n_de_country_states.res_country_state_NW').id,
            self.env.ref('l10n_de_country_states.res_country_state_RP').id,
            self.env.ref('l10n_de_country_states.res_country_state_SL').id
        ]
        if not state or state.id in state_ids:
            public_holiday_line_obj.create({
                'name': _("Corpus Christi"),
                'date': self.calculate_corpus_christi(easter),
                'variable_date': True,
                'state_ids': [(6, 0, state_ids)],
                'year_id': existing_holidays.id
            })

    @api.model
    def calculate_fixed_holidays(self, existing_holidays):
        public_holiday_line_obj = self.env['hr.holidays.public.line']

        public_holiday_line_obj.create({
            'name': _("New Years's Day"),
            'date': "%s-01-01" % existing_holidays.year,
            'variable_date': False,
            'year_id': existing_holidays.id
        })
        public_holiday_line_obj.create({
            'name': _("International Workers' Day"),
            'date': "%s-05-01" % existing_holidays.year,
            'variable_date': False,
            'year_id': existing_holidays.id
        })
        public_holiday_line_obj.create({
            'name': _("Day of German Unity"),
            'date': "%s-10-03" % existing_holidays.year,
            'variable_date': False,
            'year_id': existing_holidays.id
        })
        public_holiday_line_obj.create({
            'name': _("Christmas Day"),
            'date': "%s-12-25" % existing_holidays.year,
            'variable_date': False,
            'year_id': existing_holidays.id
        })
        public_holiday_line_obj.create({
            'name': _("Boxing Day"),
            'date': "%s-12-26" % existing_holidays.year,
            'variable_date': False,
            'year_id': existing_holidays.id
        })

    @api.model
    def calculate_state_fixed_holidays(self, existing_holidays, state=None):
        public_holiday_line_obj = self.env['hr.holidays.public.line']
        # Baden-Württemberg, Bavaria, Saxony-Anhalt
        state_ids = [
            self.env.ref('l10n_de_country_states.res_country_state_BW').id,
            self.env.ref('l10n_de_country_states.res_country_state_BY').id,
            self.env.ref('l10n_de_country_states.res_country_state_ST').id
        ]
        if not state or state.id in state_ids:
            public_holiday_line_obj.create({
                'name': _("Three Kings Day"),
                'date': "%s-01-06" % existing_holidays.year,
                'variable_date': False,
                'state_ids': [(6, 0, state_ids)],
                'year_id': existing_holidays.id
            })
        # Bavaria, Saarland
        state_ids = [
            self.env.ref('l10n_de_country_states.res_country_state_BY').id,
            self.env.ref('l10n_de_country_states.res_country_state_SL').id
        ]

        if not state or state.id in state_ids:
            public_holiday_line_obj.create({
                'name': _("Assumption Day"),
                'date': "%s-08-15" % existing_holidays.year,
                'variable_date': False,
                'state_ids': [(6, 0, state_ids)],
                'year_id': existing_holidays.id
            })
        # BB, HB, HH, MVP, NDS, SH, SN, ST, TH
        # (depends on
        # https://www.timeanddate.com/holidays/germany/reformation-day)
        state_ids = [
            self.env.ref('l10n_de_country_states.res_country_state_BB').id,
            self.env.ref('l10n_de_country_states.res_country_state_HB').id,
            self.env.ref('l10n_de_country_states.res_country_state_HH').id,
            self.env.ref('l10n_de_country_states.res_country_state_MV').id,
            self.env.ref('l10n_de_country_states.res_country_state_NI').id,
            self.env.ref('l10n_de_country_states.res_country_state_SH').id,
            self.env.ref('l10n_de_country_states.res_country_state_SN').id,
            self.env.ref('l10n_de_country_states.res_country_state_ST').id,
            self.env.ref('l10n_de_country_states.res_country_state_TH').id]

        if not state or state.id in state_ids:
            public_holiday_line_obj.create({
                'name': _("Day of Reformation"),
                'date': "%s-10-31" % existing_holidays.year,
                'variable_date': False,
                'state_ids': [(6, 0, state_ids)],
                'year_id': existing_holidays.id
            })
        # Baden-Württemberg, Bavaria,
        # North Rhine-Westphalia, Rhineland-Palatinate, Saarland
        state_ids = [
            self.env.ref('l10n_de_country_states.res_country_state_BW').id,
            self.env.ref('l10n_de_country_states.res_country_state_BY').id,
            self.env.ref('l10n_de_country_states.res_country_state_NW').id,
            self.env.ref('l10n_de_country_states.res_country_state_RP').id,
            self.env.ref('l10n_de_country_states.res_country_state_SL').id
        ]
        if not state or state.id in state_ids:
            public_holiday_line_obj.create({
                'name': _("All Saints' Day"),
                'date': "%s-11-01" % existing_holidays.year,
                'variable_date': False,
                'state_ids': [(6, 0, state_ids)],
                'year_id': existing_holidays.id
            })
        # Sachsen
        state_ids = \
            [self.env.ref('l10n_de_country_states.res_country_state_SN').id]
        if not state or state.id in state_ids:
            public_holiday_line_obj.create({
                'name': _("Repentance Day"),
                'date': "%s-11-23" % existing_holidays.year,
                'variable_date': False,
                'state_ids': [(6, 0, state_ids)],
                'year_id': existing_holidays.id
            })

    @api.multi
    def action_delete_holidays(self, existing_holidays):
        self.ensure_one()
        if existing_holidays:
            for holiday_line in existing_holidays.line_ids:
                holiday_line.unlink()
        return existing_holidays

    @api.multi
    def action_generate_de_holidays(self):
        public_holiday_obj = self.env['hr.holidays.public']

        for wizard in self:
            existing_holidays = \
                public_holiday_obj.search(
                    [('year', '=', self.year),
                     ('country_id', '=', wizard.country_id.id)]
                )
            if not existing_holidays:
                existing_holidays = \
                    public_holiday_obj.create({
                        'year': wizard.year,
                        'country_id': wizard.country_id.id})
            wizard.action_delete_holidays(existing_holidays)
            wizard.calculate_floating_holidays(existing_holidays)
            wizard.calculate_fixed_holidays(existing_holidays)
            wizard.calculate_state_floating_holidays(
                existing_holidays, state=wizard.state_id
            )
            wizard.calculate_state_fixed_holidays(
                existing_holidays, state=wizard.state_id
            )

        return {
            'type': 'ir.actions.act_window_close',
        }

    @api.multi
    def action_copy_de_holidays(self):
        public_holiday_obj = self.env['hr.holidays.public']
        public_holiday_line_obj = self.env['hr.holidays.public.line']

        for wizard in self:
            if wizard.year == wizard.template_id.year:
                raise UserError(
                    _('You cannot copy the holidays to the same year.')
                )

            # unlink all currently existing holiday lines in target year
            # before deleting target year
            existing_holidays_year_to = \
                public_holiday_obj.search([
                    ('year', '=', wizard.year),
                    ('country_id', '=', wizard.country_id.id)
                ])
            wizard.action_delete_holidays(existing_holidays_year_to)

            # create new year for holidays
            if not existing_holidays_year_to:
                new_holiday_year = \
                    public_holiday_obj.create({
                        'year': wizard.year,
                        'country_id': wizard.country_id.id
                    })
            else:
                new_holiday_year = existing_holidays_year_to[0]
            # copy fixed holidays from source year replacing the year
            for holiday in wizard.template_id.line_ids:
                if holiday.variable_date:
                    continue
                holiday_date = datetime.strptime(holiday.date, '%Y-%m-%d')
                new_holiday_date = \
                    "%s-%s-%s" % (wizard.year,
                                  holiday_date.month, holiday_date.day)
                public_holiday_line_obj.create({
                    'name': holiday.name,
                    'date': new_holiday_date,
                    'variable_date': False,
                    'state_ids': [(6, 0, [s.id for s in holiday.state_ids])],
                    'year_id': new_holiday_year.id
                })
            wizard.calculate_floating_holidays(new_holiday_year)
            wizard.calculate_state_floating_holidays(
                new_holiday_year,
                state=wizard.state_id
            )

        return {
            'type': 'ir.actions.act_window_close',
        }
