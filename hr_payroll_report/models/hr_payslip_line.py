# -*- coding: utf-8 -*-
# Copyright 2017 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class HrPayrollReport(models.Model):
    _inherit = 'hr.payslip.line'

    date_from = fields.Date(related='slip_id.date_from', store=True)
    date_to = fields.Date(related='slip_id.date_to', store=True)
    payslip_run_id = fields.Char('Payslip Batches',
                                 related='slip_id.payslip_run_id.name',
                                 store=True)
