# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime, timedelta
import time

from openerp import api, exceptions, fields, models
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DF


class HrEvaluationInterview(models.Model):
    _name = 'hr.evaluation.interview'
    _inherit = 'mail.thread'
    _rec_name = 'user_to_review_id'
    _description = 'Appraisal Interview'

    request_id = fields.Many2one(
        'survey.user_input',
        'Survey Request',
        ondelete='cascade',
        readonly=True)
    evaluation_id = fields.Many2one(
        'hr_evaluation.evaluation',
        'Appraisal Plan',
        required=True)
    phase_id = fields.Many2one(
        'hr_evaluation.plan.phase',
        'Appraisal Phase',
        required=True)
    user_to_review_id = fields.Many2one(related='evaluation_id.employee_id',
                                        string="Employee to evaluate")
    user_id = fields.Many2one(
        'res.users',
        'Interviewer')
    state = fields.Selection(
        [('draft', "Draft"),
         ('waiting_answer', "In progress"),
         ('done', "Done"),
         ('cancel', "Cancelled")],
        string="State",
        default='draft',
        required=True,
        copy=False)
    survey_id = fields.Many2one(related='phase_id.survey_id',
                                string="Appraisal Form")
    deadline = fields.Datetime(related='request_id.deadline',
                               string="Deadline")

    @api.model
    def create(self, vals):
        phase_obj = self.env['hr_evaluation.plan.phase']
        survey_id = phase_obj.browse(vals.get('phase_id')).survey_id.id

        if vals.get('user_id'):
            user_obj = self.env['res.users']
            partner_id = user_obj.browse(vals.get('user_id')).partner_id.id
        else:
            partner_id = None

        user_input_obj = self.env['survey.user_input']

        if not vals.get('deadline'):
            vals['deadline'] = (datetime.now() +
                                timedelta(days=28)).strftime(DF)

        ret = user_input_obj.create({'survey_id': survey_id,
                                     'deadline': vals.get('deadline'),
                                     'type': 'link',
                                     'partner_id': partner_id})
        vals['request_id'] = ret.id
        return super(hr_evaluation_interview, self).create(vals)

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = record.survey_id.title
            res.append((record.id, name))
        return res

    @api.multi
    def survey_req_waiting_answer(self):
        for interview in self:
            if interview.request_id:
                interview.request_id.action_survey_resent()
            interview.state = 'waiting_answer'
        return True

    @api.multi
    def survey_req_done(self):
        for id in self:
            flag = False
            wating_id = False
            if not id.evaluation_id.id:
                raise exceptions.UserError(
                    _("You cannot start evaluation without Appraisal."))
            records = id.evaluation_id.survey_request_ids
            for child in records:
                if child.state == "draft":
                    wating_id = child
                    continue
                if child.state != "done":
                    flag = True
            if not flag and wating_id:
                wating_id.survey_req_waiting_answer()
        self.write({'state': 'done'})
        return True

    @api.multi
    def survey_req_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def action_print_survey(self):
        """ If response is available then print this response 
            otherwise print survey form (print template of the survey) """
        self.ensure_one()
        return self.request_id.survey_id.with_context(
            survey_token=self.request_id.token).action_print_survey()

    @api.multi
    def action_start_survey(self):
        self.ensure_one()
        return self.request_id.survey_id.with_context(
            survey_token=self.request_id.token).action_start_survey()
