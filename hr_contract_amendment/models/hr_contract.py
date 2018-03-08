# -*- coding: utf-8 -*-
#   Copyright (C) 2018 EBII (https://www.saaslys.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _


class HrAmendmentContractChanges(models.Model):
    _name = 'hr.contract.amendment.changes'
    _description = 'HR contract amendment change'

    amendment = fields.Many2one(
        comodel_name='hr.contract.amendment', string="Amendment",
        Require=True, ondelete="cascade")
    value_name = fields.Char(string="Contract attribute name")
    value_before = fields.Char(string="Value before change")
    value_new = fields.Char(string="New value")


class HrAmendmentContract(models.Model):
    _name = 'hr.contract.amendment'
    _description = 'HR contract amendment'

    contract_id = fields.Many2one(
        comodel_name='hr.contract',string="Referenced Contract",required=True)
    amendment_number= fields.Char(string="Amendment name")
    date = fields.Date(required=True,default=fields.Date.context_today)
    user_id = fields.Many2one('res.users', string='Registred by',
                              default=lambda self: self.env.user)
    amendment_type = fields.Selection(selection=[
        ('JOB_CHANGE', _('JOB_CHANGE')),
        ('SALARY_CHANGE', _('SALARY_CHANGE')),
        ('WORKING_HOURS_CHANGE', _('WORKING_HOURS_CHANGE')),
        ('CONTRACT_SITUATION', _('CONTRACT_SITUATION')),
    ], string='Modification type')
    modifications_ids= fields.One2many(
        comodel_name="hr.contract.amendment.changes", inverse_name="amendment",
        string="Changes", required=True, )


class HrContract(models.Model):
    _inherit = 'hr.contract'

    amendment_ids = fields.One2many(
        comodel_name='hr.contract.amendment', inverse_name="contract_id",
        string="contract", required=False)

    def write(self, vals):
        sequence = self.env['ir.sequence'].next_by_code("amendment.number")
        if vals.has_key('job_id') and len(vals) == 1:
            type = 'JOB_CHANGE'
        elif vals.has_key('wage') and len(vals) == 1:
            type = 'SALARY_CHANGE'
        elif vals.has_key('working_hours') and len(vals) == 1:
            type = 'WORKING_HOURS_CHANGE'
        else:
            type = 'CONTRACT_SITUATION'

        amendmentVals = {
            'contract_id': self.id,
            'amendment_number': sequence,
            'amendment_type': type,
        }

        id_amendment= self.env['hr.contract.amendment'].create(amendmentVals)

        for k, v in vals.iteritems():
            method = getattr(self, k)
            model_field = self.env['ir.model.fields'].search(
                [('model','=','hr.contract'), ('name','=', k)])
            save = True
            if model_field.ttype == 'many2one':
                new= self.env[model_field.relation].browse(v)
                value_new= new.name
                value_before = method.name
                if value_new == value_before:
                    save = False
            else:
                value_before = method
                value_new = v

            if save or value_before != value_new:
                amendmentChangesVals = {
                    'amendment': id_amendment.id,
                    'value_name': model_field.display_name,
                    'value_before': value_before,
                    'value_new': value_new,
                }
                self.env['hr.contract.amendment.changes'].create(
                    amendmentChangesVals)
        return super(HrContract,self).write(vals)
