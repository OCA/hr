# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, fields, models


class MailChannel(models.Model):

    _inherit = 'mail.channel'

    @api.model
    def _send_badge_awards_emails(self):
        channel_general = self.env['mail.channel'].search(
            [('name', '=', 'general')], limit=1)
        partner_ids = []
        for partner_id in channel_general.channel_last_seen_partner_ids:
            partner_ids.append(str(partner_id.partner_id.id))
        partner_ids = ','.join(partner_ids)
        template = self.env.ref(
            'hr_gamification_email_notification.'
            'email_template_badge_weekly_awards')
        date_before_aweek = fields.Date.today() - timedelta(days=7)
        badge_ids = self.env['gamification.badge.user'].search(
            [('create_date', '<', fields.Date.today()),
             ('create_date', '>=', date_before_aweek)])
        if badge_ids:
            channel_general.with_context(
                {'badge_ids': badge_ids,
                 'partner_ids': partner_ids}
            ).message_post_with_template(
                template.id,
                model=self._name,
                composition_mode='mass_mail'
            )

        return True
