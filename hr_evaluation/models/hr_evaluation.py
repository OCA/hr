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

from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil import parser
import time

from openerp import api, exceptions, fields, models
from openerp.tools.translate import _


class EvaluationPlan(models.Model):
    _name = "hr_evaluation.plan"
    _description = "Appraisal Plan"

    name = fields.Char("Appraisal Plan", required=True)
    company_id = fields.Many2one(
        'res.company',
        'Company',
        default=lambda s: s.env.user.company_id,
        required=True)
    phase_ids = fields.One2many(
        'hr_evaluation.plan.phase', 'plan_id', 'Appraisal Phases', copy=True)
    month_first = fields.Integer(
        'First Appraisal in (months)',
        default=6,
        help="This number of months will be used "
             "to schedule the first evaluation date of the employee "
             "when selecting an evaluation plan. ")
    month_next = fields.Integer(
        'Periodicity of Appraisal (months)',
        default=12,
        help="The number of month that depicts "
             "the delay between each evaluation of this plan "
             "(after the first one).")
    active = fields.Boolean('Active', default=True)


class EvaluationPlanPhase(models.Model):
    _name = "hr_evaluation.plan.phase"
    _description = "Appraisal Plan Phase"
    _order = "sequence"
    name = fields.Char("Phase", required=True)
    sequence = fields.Integer("Sequence", default=1)
    company_id = fields.Many2one(
        related='plan_id.company_id',
        string='Company',
        store=True,
        readonly=True)
    plan_id = fields.Many2one(
        'hr_evaluation.plan', 'Appraisal Plan', ondelete='cascade')
    action = fields.Selection(
        [('top-down', 'Top-Down Appraisal Requests'),
         ('bottom-up', 'Bottom-Up Appraisal Requests'),
         ('self', 'Self Appraisal Requests'),
         ('final', 'Final Interview')],
        'Action',
        required=True)
    survey_id = fields.Many2one(
        'survey.survey', 'Appraisal Form', required=True)
    send_answer_manager = fields.Boolean(
        'All Answers',
        help="Send all answers to the manager")
    send_answer_employee = fields.Boolean(
        'All Answers',
        help="Send all answers to the employee")
    send_anonymous_manager = fields.Boolean(
        'Anonymous Summary',
        help="Send an anonymous summary to the manager")
    send_anonymous_employee = fields.Boolean(
        'Anonymous Summary',
        help="Send an anonymous summary to the employee")
    wait = fields.Boolean(
        'Wait Previous Phases',
        help="Check this box if you want to wait that all preceding phases "
             "are finished before launching this phase.")
    mail_feature = fields.Boolean(
        'Send mail for this phase',
        help="Check this box if you want to send mail "
             "to employees coming under this phase")
    mail_body = fields.Text(
        'Email',
        default=lambda s: _("""
Date: %(date)s

Dear %(employee_name)s,

I am doing an evaluation regarding %(eval_name)s.

Kindly submit your response.


Thanks,
--
%(user_signature)s

        """))
    email_subject = fields.Text(
        'Subject',
        default=lambda s: _('''Regarding '''))


class Employee(models.Model):
    _name = "hr.employee"
    _inherit = "hr.employee"

    def _compute_appraisal_count(self):
        Eval = self.env['hr.evaluation.interview']
        for empl in self:
            empl.appraisal_count = Eval.search_count(
                [('user_to_review_id', '=', empl.id)])

    evaluation_plan_id = fields.Many2one(
        'hr_evaluation.plan', 'Appraisal Plan')
    evaluation_date = fields.Date(
        'Next Appraisal Date',
        help="The date of the next appraisal "
             "is computed by the appraisal plan's dates "
             "(first appraisal + periodicity).")
    appraisal_count = fields.Integer(
        compute=_compute_appraisal_count,
        string='Appraisal Interviews')

    @api.model
    def run_employee_evaluation(self):  # cronjob
        now = parser.parse(datetime.now().strftime('%Y-%m-%d'))
        obj_evaluation = self.env['hr_evaluation.evaluation']
        emp_ids = self.search([('evaluation_plan_id', '<>', False),
                               ('evaluation_date', '=', False)])
        for emp in emp_ids:
            first_date = (
                now +
                relativedelta(months=emp.evaluation_plan_id.month_first)
                ).strftime('%Y-%m-%d')
            emp.evaluation_date = first_date

        emp_ids = self.search([
            ('evaluation_plan_id', '<>', False),
            ('evaluation_date', '<=', time.strftime("%Y-%m-%d"))
            ])
        for emp in emp_ids:
            next_date = (
                now +
                relativedelta(months=emp.evaluation_plan_id.month_next)
                ).strftime('%Y-%m-%d')
            emp.evaluation_date = next_date
            plan_id = obj_evaluation.create(
                {'employee_id': emp.id,
                 'plan_id': emp.evaluation_plan_id.id})
            plan_id.button_plan_in_progress()
        return True


class Evaluation(models.Model):
    _name = "hr_evaluation.evaluation"
    _inherit = "mail.thread"
    _description = "Employee Appraisal"
    _rec_name = "employee_id"
    date = fields.Date(
        "Appraisal Deadline",
        default=lambda *a: (
            parser.parse(datetime.now().strftime('%Y-%m-%d')) +
            relativedelta(months=+1)
            ).strftime('%Y-%m-%d'),
        required=True,
        index=True)
    employee_id  = fields.Many2one('hr.employee', "Employee", required=True)
    note_summary = fields.Text('Appraisal Summary')
    note_action = fields.Text(
        'Action Plan',
        help="If the evaluation does not meet the expectations, "
             "you can propose an action plan")
    rating = fields.Selection(
        [('0', 'Significantly below expectations'),
         ('1', 'Do not meet expectations'),
         ('2', 'Meet expectations'),
         ('3', 'Exceeds expectations'),
         ('4', 'Significantly exceeds expectations')],
        "Appreciation",
        help="This is the appreciation on which the evaluation is summarized."
        )
    survey_request_ids = fields.One2many(
        'hr.evaluation.interview', 'evaluation_id', 'Appraisal Forms')
    plan_id = fields.Many2one(
        'hr_evaluation.plan', 'Plan', required=True)
    state = fields.Selection(
        [('draft', 'New'),
         ('cancel', 'Cancelled'),
         ('wait', 'Plan In Progress'),
         ('progress', 'Waiting Appreciation'),
         ('done', 'Done')],
        'Status',
        default='draft',
        required=True,
        readonly=True,
        copy=False)
    date_close = fields.Date('Ending Date', index=True)

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = record.plan_id.name
            employee = record.employee_id.name_related
            res.append((record.id, name + ' / ' + employee))
        return res

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.plan_id = False
        if (self.employee_id and 
                self.employee_id.evaluation_plan_id and 
                self.employee_id.evaluation_plan_id.id):
            self.plan_id = self.employee_id.evaluation_plan_id

    @api.multi
    def button_plan_in_progress(self):
        hr_eval_inter_obj = self.env['hr.evaluation.interview']
        for evaluation in self:
            wait = False
            for phase in evaluation.plan_id.phase_ids:
                children = []
                if phase.action == "bottom-up":
                    children = evaluation.employee_id.child_ids
                elif phase.action in ("top-down", "final"):
                    if evaluation.employee_id.parent_id:
                        children = [evaluation.employee_id.parent_id]
                elif phase.action == "self":
                    children = [evaluation.employee_id]

                for child in children:
                    int_id = hr_eval_inter_obj.create({
                        'evaluation_id': evaluation.id,
                        'phase_id': phase.id,
                        'deadline': (
                            parser.parse(datetime.now().strftime('%Y-%m-%d'))
                            + relativedelta(months=+1)).strftime('%Y-%m-%d'),
                        'user_id': child.user_id.id,
                    })
                    if phase.wait:
                        wait = True
                    if not wait:
                        int_id.survey_req_waiting_answer()

                    if (not wait) and phase.mail_feature:
                        body = phase.mail_body % {
                            'employee_name': child.name,
                            'user_signature': child.user_id.signature,
                            'eval_name': phase.survey_id.title,
                            'date': time.strftime('%Y-%m-%d'),
                            'time': time
                            }
                        sub = phase.email_subject
                        if child.work_email:
                            vals = {'state': 'outgoing',
                                    'subject': sub,
                                    'body_html': '<pre>%s</pre>' % body,
                                    'email_to': child.work_email,
                                    'email_from':
                                        evaluation.employee_id.work_email}
                            self.env['mail.mail'].create(vals)

        self.write({'state': 'wait'})
        return True

    @api.multi
    def button_final_validation(self):
        request_obj = self.env['hr.evaluation.interview']
        self.write({'state': 'progress'})
        for evaluation in self:
            if (evaluation.employee_id and 
                    evaluation.employee_id.parent_id and 
                    evaluation.employee_id.parent_id.user_id):
                self.message_subscribe_users(
                    user_ids=[evaluation.employee_id.parent_id.user_id.id])
            if len(evaluation.survey_request_ids) != len(request_obj.search([
                    ('evaluation_id', '=', evaluation.id), 
                    ('state', 'in', ['done', 'cancel'])])):
                raise exceptions.UserError(
                    _("You cannot change state, because"
                      " some appraisal forms have not been completed."))
        return True

    @api.multi
    def button_done(self):
        self.write({'state': 'done', 'date_close': time.strftime('%Y-%m-%d')})
        return True

    @api.multi
    def button_cancel(self):
        self.ensure_one()
        for r in self.survey_request_ids:
            r.survey_req_cancel()
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def button_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def write(self, vals):
        if vals.get('employee_id'):
            employee_id = self.env['hr.employee'].browse(
                vals.get('employee_id'))
            if employee_id.parent_id and employee_id.parent_id.user_id:
                vals['message_follower_ids'] = [
                    (4, employee_id.parent_id.user_id.partner_id.id)]
        if 'date' in vals:
            new_vals = {'deadline': vals.get('date')}
            for evaluation in self:
                evaluation.survey_request_ids.write(new_vals)

        return super(Evaluation, self).write(vals)
