# -*- coding: utf-8 -*-
# Author: Denis Leemann
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    same_candidate_application_ids = fields.Many2many(
        'hr.applicant',
        string='Same candidates',
        compute='_compute_same_candidate_application_count',
        readonly=True,
    )
    same_candidate_application_count = fields.Integer(
        'Number of similar candidates',
        compute='_compute_same_candidate_application_count',
        readonly=True,
    )

    @api.depends('email_from', 'partner_phone')
    def _compute_same_candidate_application_count(self):
        for applicant in self:
            domain = ['|', '&', ('email_from', '=', applicant.email_from),
                      ('email_from', '!=', False), '&',
                      ('partner_phone', '=', applicant.partner_phone),
                      ('partner_phone', '!=', False)]
            if not isinstance(applicant.id, models.NewId):
                domain = [('id', '!=', applicant.id)] + domain
            same_apps = self.with_context(active_test=False).search(domain)
            applicant.same_candidate_application_ids = same_apps
            applicant.same_candidate_application_count = len(same_apps)

    def action_view_applicants(self):
        action = self.env.ref('hr_recruitment.crm_case_categ0_act_job')
        result = action.read()[0]
        result['domain'] = [('id', 'in',
                            self.same_candidate_application_ids.ids)]
        result['context'] = {'active_test': False, }
        return result
