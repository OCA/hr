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
from dateutil.relativedelta import relativedelta
from dateutil import parser
import time

from openerp import api, fields, models
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DF


class hr_evaluation_interview(osv.Model):
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
    user_to_review_id = fields.related('evaluation_id', 'employee_id', type="many2one", relation="hr.employee", string="Employee to evaluate"),
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
    survey_id = fields.related('phase_id', 'survey_id', string="Appraisal Form", type="many2one", relation="survey.survey"),
    deadline = fields.related('request_id', 'deadline', type="datetime", string="Deadline"),

    @api.model
    def create(self, vals):
        phase_obj = self.env.get('hr_evaluation.plan.phase')
        survey_id = phase_obj.read(cr, uid, vals.get('phase_id'), fields=['survey_id'], context=context)['survey_id'][0]

        if vals.get('user_id'):
            user_obj = self.pool.get('res.users')
            partner_id = user_obj.read(cr, uid, vals.get('user_id'), fields=['partner_id'], context=context)['partner_id'][0]
        else:
            partner_id = None

        user_input_obj = self.pool.get('survey.user_input')

        if not vals.get('deadline'):
            vals['deadline'] = (datetime.now() + timedelta(days=28)).strftime(DF)

        ret = user_input_obj.create(cr, uid, {'survey_id': survey_id,
                                            'deadline': vals.get('deadline'),
                                            'type': 'link',
                                            'partner_id': partner_id}, context=context)
        vals['request_id'] = ret
        return super(hr_evaluation_interview, self).create(cr, uid, vals, context=context)

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.browse(cr, uid, ids, context=context)
        res = []
        for record in reads:
            name = record.survey_id.title
            res.append((record['id'], name))
        return res

    def survey_req_waiting_answer(self, cr, uid, ids, context=None):
        request_obj = self.pool.get('survey.user_input')
        for interview in self.browse(cr, uid, ids, context=context):
            if interview.request_id:
                request_obj.action_survey_resent(cr, uid, [interview.request_id.id], context=context)
            self.write(cr, uid, interview.id, {'state': 'waiting_answer'}, context=context)
        return True

    def survey_req_done(self, cr, uid, ids, context=None):
        for id in self.browse(cr, uid, ids, context=context):
            flag = False
            wating_id = 0
            if not id.evaluation_id.id:
                raise osv.except_osv(_('Warning!'), _("You cannot start evaluation without Appraisal."))
            records = id.evaluation_id.survey_request_ids
            for child in records:
                if child.state == "draft":
                    wating_id = child.id
                    continue
                if child.state != "done":
                    flag = True
            if not flag and wating_id:
                self.survey_req_waiting_answer(cr, uid, [wating_id], context=context)
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return True

    def survey_req_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        return True

    def action_print_survey(self, cr, uid, ids, context=None):
        """ If response is available then print this response otherwise print survey form (print template of the survey) """
        context = dict(context or {})
        interview = self.browse(cr, uid, ids, context=context)[0]
        survey_obj = self.pool.get('survey.survey')
        response_obj = self.pool.get('survey.user_input')
        response = response_obj.browse(cr, uid, interview.request_id.id, context=context)
        context.update({'survey_token': response.token})
        return survey_obj.action_print_survey(cr, uid, [interview.survey_id.id], context=context)

    def action_start_survey(self, cr, uid, ids, context=None):
        context = dict(context or {})
        interview = self.browse(cr, uid, ids, context=context)[0]
        survey_obj = self.pool.get('survey.survey')
        response_obj = self.pool.get('survey.user_input')
        # grab the token of the response and start surveying
        response = response_obj.browse(cr, uid, interview.request_id.id, context=context)
        context.update({'survey_token': response.token})
        return survey_obj.action_start_survey(cr, uid, [interview.survey_id.id], context=context)
