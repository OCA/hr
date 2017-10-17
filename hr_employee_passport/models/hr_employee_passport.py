# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrEmployeePassport(models.Model):

    _name = 'hr.employee.passport'
    _inherit = 'mail.thread'
    _description = 'Employee Passport'
    _order = 'end_date desc'

    name = fields.Char(
        compute='_compute_name',
        store=True,
    )
    description = fields.Char()
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string="Employee",
        required=True,
        ondelete='cascade',
    )
    end_date = fields.Date(
        string="Expiration date",
        required=True,
        track_visibility='onchange',
    )
    passport_file = fields.Binary(
        string="Passport",
        attachment=True,
        required=True,
    )
    passport_filename = fields.Char()
    is_valid = fields.Boolean(
        compute='_compute_is_valid',
        search='_search_is_valid',
    )

    @api.multi
    @api.depends(
        'employee_id.name',
        'end_date'
    )
    def _compute_name(self):
        for rec in self:
            rec.name = '%s (%s)' % (
                rec.employee_id.name,
                rec.end_date,
            )

    @api.multi
    def _compute_is_valid(self):
        today_date = fields.Date.today()
        for rec in self:
            rec.is_valid = today_date <= rec.end_date

    @api.model
    def _search_is_valid(self, operator, value):
        """
        This method only handles '=' and '!=' operator
        """
        search_valid = (
            operator == '=' and value or
            operator == '!=' and not value
        )
        today_date = fields.Date.today()

        if search_valid:
            domain = [
                ('end_date', '>=', today_date)
            ]
        else:
            domain = [
                ('end_date', '<=', today_date),
            ]
        return domain
