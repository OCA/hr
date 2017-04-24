# -*- coding: utf-8 -*-
# Copyright 2017 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import fields, osv


class HrPayrollReport(osv.osv):
    _inherit = 'hr.payslip.line'

    _columns = {
        'date_from': fields.date('Date From', related='slip_id.date_from'),
        'date_to': fields.date('Date To', related='slip_id.date_to'),
        'payslip_run_id': fields.char('Payslip Batches',
                                      related='slip_id.payslip_run_id.name'),
    }
