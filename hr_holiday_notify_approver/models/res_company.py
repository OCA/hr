# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    leave_notify_approver = fields.Selection(
        selection=[('none', "Don't notify anyone."),
                   ('manager', "Notify employee's manager."),
                   ('department', "Notify employee's department manager."),
                   ('default', "Notify HR managers.")],
        string='Email Notification on Leave Request',
        default='none')
