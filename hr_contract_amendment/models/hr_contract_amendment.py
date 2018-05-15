# -*- coding: utf-8 -*-
#   Copyright (C) 2018 EBII (https://www.saaslys.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, _


class HrContractAmendmentChanges(models.Model):
    _name = 'hr.contract.amendment.changes'
    _description = 'HR contract amendment change'

    amendment_id = fields.Many2one(
        comodel_name='hr.contract.amendment', string="Amendment",
        required=True, ondelete="cascade")
    value_name = fields.Char(string="Contract attribute name")
    value_before = fields.Char(string="Value before change")
    value_new = fields.Char(string="New value")


class HrContractAmendment(models.Model):
    _name = 'hr.contract.amendment'
    _description = 'HR contract amendment'

    contract_id = fields.Many2one(
        comodel_name='hr.contract', string="Referenced Contract",
        required=True)
    name = fields.Char(string="Amendment name")
    effective_date = fields.Date(string="Effective Date")
    date = fields.Date(required=True, default=fields.Date.context_today)
    user_id = fields.Many2one('res.users', string='Registered by',
                              default=lambda self: self.env.user)
    amendment_type = fields.Selection(selection=[
        ('JOB_CHANGE', _('JOB_CHANGE')),
        ('SALARY_CHANGE', _('SALARY_CHANGE')),
        ('WORKING_HOURS_CHANGE', _('WORKING_HOURS_CHANGE')),
        ('CONTRACT_SITUATION', _('CONTRACT_SITUATION')),
    ], string='Modification type')
    modifications_ids = fields.One2many(
        comodel_name="hr.contract.amendment.changes",
        inverse_name="amendment_id", string="Changes", required=True, )
